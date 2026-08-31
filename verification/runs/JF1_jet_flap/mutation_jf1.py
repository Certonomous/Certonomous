#!/usr/bin/env python3
"""
JF1 -- THE FATAL-CLAUSE CONTROL: section 8.2's TEN mutation limbs (:1706-1731).

"Each mutates exactly one clause on a byte-level copy of a real completed case
and REQUIRES THE COMPARATOR TO REFUSE.  A limb that does not produce a refusal
means that clause is not enforced and the whole comparator is NOT A RESULT
until it is." (:1709-1712)

THIS HARNESS RUNS EVERY LIMB THROUGH THE PRODUCTION CLI IN A FRESH SUBPROCESS
(`python3 analyse_jf1.py --completion ...`), so what is measured is the real
exit code of the real comparator, not an in-process call that could be shadowed
by stale bytecode.  `__pycache__` is cleared before every limb regardless
(stale bytecode has INVERTED mutation tests in this lab).

EACH LIMB ASSERTS A SPECIFIC REFUSAL CODE, NEVER MERELY `exit 2`.  A limb that
accepts any refusal would stay green when the comparator refuses for an
unrelated reason, which is the failure mode a mutation limb exists to exclude.

-------------------------------------------------------------------------------
THE SUBSTRATE, AND ITS LIMITATION, STATED BEFORE ANY RESULT IS REPORTED
-------------------------------------------------------------------------------
The five completed rows under `verification/runs/JF1_jet_flap/` are REAL
OpenFOAM trees -- real `log.simpleFoam`, real fields, real `postProcessing`.
They are also FEASIBILITY rows and they do NOT satisfy the registered shape of
section 8.1 as they stand:

  (a) `endTime 8000` / `writeInterval 1000`, not the pinned 20000 / 20000;
  (b) `RUN_STATUS` sits at the CASE ROOT in a whitespace format, not at the
      registered `artefacts/RUN_STATUS.<case_id>.txt` in `key=value` form;
  (c) NO JF1 RUN ON THIS BOX HAS EVER CONVERGED.  At iteration 8000 the initial
      residuals are Uy 3.63e-06, k 2.55e-05, p 1.27e-05 -- all ABOVE the
      registered 1e-6 -- so no run carries a `SIMPLE solution converged` line
      and no run can satisfy branch 3a on its own evidence.

`prepare_registered_copy` therefore performs a NAMED, RECORDED PREPARATION on
the copy before any limb runs: it brings the copy to the registered shape and
SYNTHESISES the converged-termination signature (c).  Every preparation step is
listed in the artefact.  THE POSITIVE CONTROL IS A PASS ON A PREPARED COPY, NOT
ON A JF1 RESULT, and nothing in this harness is a JF1 measurement.  The
mutation is then exactly one further edit on top of the prepared copy, so a
limb's refusal is attributable to the mutation and to nothing else.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED[R-DASH-O]: mutation_jf1.py must not run under -O\n")
    sys.exit(2)

import os
import re
import json
import shutil
import argparse
import datetime
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, os.pardir, os.pardir))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import foam_io_jf1 as FIO                                   # noqa: E402

COMPARATOR = os.path.join(HERE, "analyse_jf1.py")
DEFAULT_SUBSTRATE = os.path.join(REPO, "verification", "runs", "JF1_jet_flap",
                                 "JF1_L1_BLOWN_CMU010_A0")
ARTEFACT_DIR = os.path.join(REPO, "verification", "runs", "JF1_jet_flap", "artefacts")


class HarnessError(Exception):
    pass


def clear_pycache():
    """Stale bytecode has inverted mutation tests in this lab: the clean control
    fails and the mutated case passes.  PYTHONDONTWRITEBYTECODE does NOT fix it."""
    for d in (HERE, os.path.join(REPO, "scripts")):
        p = os.path.join(d, "__pycache__")
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)


def rewrite(path, fn):
    """Read, transform, write -- IN THAT ORDER.

    `open(p, "w").write(open(p).read()...)` evaluates `open(p, "w")` FIRST and
    TRUNCATES the file, so the inner read returns an empty string and the
    mutation becomes `delete the whole file`.  Caught here by the limbs
    refusing with the right CODE for the WRONG REASON -- M1 reported `no
    solver_rc key` instead of `solver_rc = 137`, M3 reported every pin key
    absent instead of `endTime = 15000`.  A limb that refuses for a reason
    other than its own mutation is not a control over its clause."""
    text = open(path).read()
    out = fn(text)
    if out == text:
        raise HarnessError("mutation on %s changed nothing" % path)
    with open(path, "w") as fh:
        fh.write(out)
    return out

def run_comparator(case_dir, case_id):
    """The PRODUCTION PATH: a fresh interpreter, the real CLI, the real exit
    code.  Returns (rc, refusal_code, stderr_tail)."""
    clear_pycache()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, COMPARATOR, "--completion", case_dir, "--case-id", case_id],
        capture_output=True, text=True, env=env, cwd=REPO)
    m = re.search(r"REFUSED\[([A-Z0-9\-]+)\]", proc.stderr)
    tail = (proc.stderr.strip().splitlines() or [""])[0][:400]
    return proc.returncode, (m.group(1) if m else None), tail


# ===========================================================================
# PREPARATION -- named, recorded, and separate from every mutation
# ===========================================================================
CONVERGED_LINE = "SIMPLE solution converged in %d iterations"


def _final_block_split(text, n):
    marker = "\nTime = %d\n" % n
    i = text.rfind(marker)
    if i < 0:
        raise HarnessError("no final `Time = %d` block in the log" % n)
    return text[:i + len(marker)], text[i + len(marker):]


def _drive_residuals_below(tail, factor=100.0):
    """Rewrite the final iteration's initial residuals so branch 3a's
    `< 1e-6` clause can be satisfied.  PART OF THE PREPARATION, NOT OF ANY
    MUTATION: no JF1 run on this box converged, so without this step the
    positive control cannot exist and every limb would be vacuous."""
    changed = {}
    for name in ("Ux", "Uy", "k", "omega", "p"):
        pat = re.compile(r"(Solving for %s, Initial residual = )([0-9eE+.\-]+)" % name)
        m = pat.search(tail)
        if not m:
            raise HarnessError("no `Solving for %s` in the final block" % name)
        old = float(m.group(2))
        new = old / factor
        if new >= 1e-6:
            new = 1e-9
        changed[name] = (old, new)
        tail = tail[:m.start()] + m.group(1) + ("%.9e" % new) + tail[m.end():]
    return tail, changed


def prepare_registered_copy(src, dst, case_id):
    """Byte-level copy, then bring it to the registered shape of section 8.1.
    Returns the list of preparation steps taken, for the artefact."""
    FIO.byte_copy_case(src, dst)
    steps = ["byte-level copy (shutil.copytree, mtimes preserved) of %s" % src]

    ns, dirs = FIO.n_stop(dst)
    if ns is None:
        raise HarnessError("%s has no time directory to prepare" % src)
    n = int(float(ns))

    # P1 -- under the pinned `writeInterval 20000` a conforming run writes ONLY
    # `0` and `N_stop`.  The substrate's intermediate directories are an artifact
    # of its own `writeInterval 1000` and cannot exist under the registration.
    removed = []
    for d in dirs[:-1]:
        shutil.rmtree(os.path.join(dst, d))
        removed.append(d)
    steps.append("P1 removed %d intermediate time directories (%s..%s); under the "
                 "pinned writeInterval 20000 only `0` and `N_stop` exist"
                 % (len(removed), removed[0] if removed else "-",
                    removed[-1] if removed else "-"))

    # P2 -- the section 8.1 clause 3 pin.
    cdp = os.path.join(dst, "system", "controlDict")
    txt = open(cdp).read()
    txt2 = re.sub(r"^(\s*endTime\s+)\d+;", r"\g<1>20000;", txt, count=1, flags=re.M)
    txt2 = re.sub(r"^(\s*writeInterval\s+)\d+;", r"\g<1>20000;", txt2, count=1, flags=re.M)
    if txt2 == txt:
        raise HarnessError("controlDict pin edit changed nothing")
    open(cdp, "w").write(txt2)
    steps.append("P2 system/controlDict endTime 8000 -> 20000, top-level "
                 "writeInterval 1000 -> 20000 (section 8.1 clause 3 pin, :1615)")

    # P3 -- the converged-termination signature.  SYNTHESISED: see the module
    # docstring, limitation (c).
    lp = os.path.join(dst, "log.simpleFoam")
    text = open(lp).read()
    head, tail = _final_block_split(text, n)
    tail, changed = _drive_residuals_below(tail)
    if not re.search(r"^End\s*$", tail, re.M):
        raise HarnessError("no `End` line in the final block to insert before")
    tail = re.sub(r"^End\s*$", (CONVERGED_LINE % n) + "\nEnd", tail, count=1, flags=re.M)
    open(lp, "w").write(head + tail)
    steps.append("P3 SYNTHESISED the 3a signature: final-iteration initial residuals "
                 "driven below 1e-6 (%s) and `%s` inserted before `End`. NO JF1 RUN "
                 "ON THIS BOX EVER CONVERGED; without this step no positive control "
                 "exists and every limb is vacuous."
                 % ({k: "%.3e->%.3e" % v for k, v in changed.items()},
                    CONVERGED_LINE % n))

    # P4 -- the registered RUN_STATUS path and format (section 9.2/9.3).
    art = os.path.join(dst, "artefacts")
    if not os.path.isdir(art):
        os.makedirs(art)
    open(os.path.join(art, "RUN_STATUS.%s.txt" % case_id), "w").write(
        "solver_rc=0\nend=%s\ncase_id=%s\nnote=exit-status-of-simpleFoam-itself\n"
        % (datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), case_id))
    steps.append("P4 wrote artefacts/RUN_STATUS.%s.txt in the section 9.2 key=value "
                 "form; the substrate's root-level whitespace RUN_STATUS is NOT at "
                 "the registered path (:1807-1810)" % case_id)

    # P5 -- the age datum.  `0/U` is touched LAST at launch (:1783), so every
    # field at N_stop must be strictly newer.  Made explicit rather than relying
    # on the copy's inherited mtimes.
    base = 1_700_000_000.0
    os.utime(os.path.join(dst, "0", "U"), (base, base))
    for f in os.listdir(os.path.join(dst, ns)):
        p = os.path.join(dst, ns, f)
        if os.path.isfile(p):
            os.utime(p, (base + 10, base + 10))
    steps.append("P5 set 0/U mtime strictly older than every field in %s/ (clause 6 "
                 "age guard, :1666)" % ns)
    return dict(n_stop=n, steps=steps, case_dir=dst)


# ===========================================================================
# THE TEN LIMBS (:1714-1725)
# ===========================================================================
def m1(case, case_id):
    """M1 | 8.1(1) | `solver_rc` set non-zero in `artefacts/RUN_STATUS.*` | refuse"""
    p = FIO.run_status_path(case, case_id)
    rewrite(p, lambda t: t.replace("solver_rc=0", "solver_rc=137"))
    return "R-COMPLETION-1-RC"


def m2(case, case_id):
    """M2 | 8.1(2) | the `End` line removed from `log.simpleFoam` | refuse"""
    p = os.path.join(case, "log.simpleFoam")
    rewrite(p, lambda t: re.sub(r"^End\s*$\n?", "", t, flags=re.M))
    return "R-COMPLETION-2-END"


def m3(case, case_id):
    """M3 | 8.1(3) pin | `endTime` 20000 -> 15000 in `system/controlDict` | refuse"""
    p = os.path.join(case, "system", "controlDict")
    rewrite(p, lambda t: re.sub(r"^(\s*endTime\s+)20000;", r"\g<1>15000;",
                                t, count=1, flags=re.M))
    return "R-PIN-CONTROLDICT"


def m4(case, case_id):
    """M4 | 8.1(3) pin | `residualControl { p }` 1e-6 -> 1e-4 in `fvSolution` | refuse"""
    p = os.path.join(case, "system", "fvSolution")
    rewrite(p, lambda t: re.sub(r"(residualControl\s*\{[^}]*?\bp\s+)1e-0?6;",
                                r"\g<1>1e-04;", t, count=1, flags=re.S))
    return "R-PIN-FVSOLUTION"


def m5(case, case_id):
    """M5 | 8.1(3a) | the converged line's iteration number changed so it no
    longer equals `N_stop` | refuse"""
    p = os.path.join(case, "log.simpleFoam")
    m = re.search(r"SIMPLE solution converged in (\d+) iterations", open(p).read())
    if not m:
        raise HarnessError("M5: no converged line to mutate")
    n = int(m.group(1))
    rewrite(p, lambda t: t.replace(m.group(0), CONVERGED_LINE % (n - 1)))
    return "R-TERM-3A-N-MISMATCH"


def m6(case, case_id):
    """M6 | 8.1(3a) | the time directory renamed so `N_stop` < 2000 (the plateau
    window is absent) | refuse

    The rename alone would leave the log claiming 8000 iterations and a
    converged line naming 8000, so TWO further clauses would fail and the
    refusal would not be attributable to the 2 000 floor.  The limb therefore
    makes the copy otherwise CONSISTENT at N = 1900 -- log truncated, converged
    line renamed, residuals re-driven -- so the floor is the ONLY clause left
    failing.  Isolating the clause is what makes the limb a control."""
    target = 1900
    ns, _ = FIO.n_stop(case)
    n = int(float(ns))
    p = os.path.join(case, "log.simpleFoam")
    text = open(p).read()
    marker = "\nTime = %d\n" % (target + 1)
    i = text.find(marker)
    if i < 0:
        raise HarnessError("M6: no `Time = %d` to truncate at" % (target + 1))
    head, tail = _final_block_split(text[:i], target)
    tail, _ = _drive_residuals_below(tail)
    open(p, "w").write(head + tail + (CONVERGED_LINE % target) + "\nEnd\n")
    os.rename(os.path.join(case, ns), os.path.join(case, str(target)))
    return "R-TERM-3A-BELOW-2000"


def m7(case, case_id):
    """M7 | 8.1(3b) THE CAP | time directory renamed to `20000` and the
    converged line deleted | refuse, LABELLED CAP HIT"""
    ns, _ = FIO.n_stop(case)
    p = os.path.join(case, "log.simpleFoam")
    rewrite(p, lambda t: re.sub(r"SIMPLE solution converged in \d+ iterations\n",
                                "", t))
    os.rename(os.path.join(case, ns), os.path.join(case, "20000"))
    return "R-TERM-3B-CAP"


def m8(case, case_id):
    """M8 | 8.1(3c) THE EARLY STOP | the converged line deleted, `End` retained,
    `rc = 0` retained, `N_stop` left below 20000 -- THE EXACT SIGNATURE OF A
    KILLED OR TIMED-OUT RUN THAT STILL LOOKS TIDY | refuse

    ":1727 -- M8 is the limb that matters most and it is registered as such.  It
    is the case that the struck clause 3 would have caught BY ACCIDENT, and that
    a naively loosened clause 3 would let through."""
    p = os.path.join(case, "log.simpleFoam")
    rewrite(p, lambda t: re.sub(r"SIMPLE solution converged in \d+ iterations\n",
                                "", t))
    return "R-TERM-3C-EARLY-STOP"


def m9a(case, case_id):
    """M9 | 8.1(4) | one field deleted from `N_stop/` | refuse"""
    ns, _ = FIO.n_stop(case)
    os.remove(os.path.join(case, ns, "nut"))
    return "R-COMPLETION-4-FIELDS"


def m9b(case, case_id):
    """M9 | 8.1(5) | one `ExecutionTime` line removed | refuse"""
    p = os.path.join(case, "log.simpleFoam")
    def drop_one(text):
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            if line.startswith("ExecutionTime = "):
                del lines[i]
                return "".join(lines)
        raise HarnessError("M9b: no ExecutionTime line to remove")
    rewrite(p, drop_one)
    return "R-COMPLETION-5-EXECTIME"


def m10(case, case_id):
    """M10 | 8.1(6) | `0/U` touched AFTER the `N_stop` fields, to trip the age
    guard | refuse"""
    ns, _ = FIO.n_stop(case)
    newest = max(os.path.getmtime(os.path.join(case, ns, f))
                 for f in os.listdir(os.path.join(case, ns))
                 if os.path.isfile(os.path.join(case, ns, f)))
    os.utime(os.path.join(case, "0", "U"), (newest + 60, newest + 60))
    return "R-COMPLETION-6-AGE"


LIMBS = [("M1", "8.1(1) rc", m1), ("M2", "8.1(2) End", m2),
         ("M3", "8.1(3) pin controlDict", m3), ("M4", "8.1(3) pin fvSolution", m4),
         ("M5", "8.1(3a) converged N != N_stop", m5),
         ("M6", "8.1(3a) N_stop < 2000", m6),
         ("M7", "8.1(3b) THE CAP", m7), ("M8", "8.1(3c) THE EARLY STOP", m8),
         ("M9a", "8.1(4) field deleted", m9a),
         ("M9b", "8.1(5) ExecutionTime line removed", m9b),
         ("M10", "8.1(6) age guard", m10)]


# ===========================================================================
# THE HARNESS
# ===========================================================================
def run_all(substrate, case_id, workroot):
    out = dict(substrate=substrate, case_id=case_id,
               utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))

    # ---- THE POSITIVE CONTROL.  Without it every limb is vacuous.
    clean = os.path.join(workroot, "clean")
    prep = prepare_registered_copy(substrate, clean, case_id)
    out["preparation"] = prep["steps"]
    rc, code, tail = run_comparator(clean, case_id)
    out["positive_control"] = dict(rc=rc, refusal_code=code, stderr=tail,
                                   passed=(rc == 0 and code is None))
    if rc != 0:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("the PREPARED CLEAN COPY does not pass section 8.1 (rc = %d, "
                      "%s). Every mutation limb below would refuse for that reason "
                      "and would test nothing." % (rc, code))
        return out

    # ---- THE TEN LIMBS
    results = []
    for name, clause, fn in LIMBS:
        work = os.path.join(workroot, name)
        prepare_registered_copy(substrate, work, case_id)
        want = fn(work, case_id)
        rc, code, tail = run_comparator(work, case_id)
        ok = (rc == 2 and code == want)
        results.append(dict(limb=name, clause=clause, required="refuse",
                            expected_code=want, rc=rc, refusal_code=code,
                            stderr=tail, passed=bool(ok)))
    out["limbs"] = results
    failed = [r["limb"] for r in results if not r["passed"]]
    out["failed_limbs"] = failed
    if failed:
        out["verdict"] = "NOT A RESULT"
        out["why"] = ("limbs %s did not refuse with their registered clause's code. "
                      ":1711 -- a limb that does not produce a refusal means that "
                      "clause is not enforced and the whole comparator is NOT A "
                      "RESULT until it is." % failed)
    else:
        out["verdict"] = "GATE REACHED"
        out["why"] = ("the prepared clean copy PASSES section 8.1 and all %d mutation "
                      "limbs REFUSE with the specific refusal code of the clause each "
                      "mutates." % len(results))
    return out


def run_plants(substrate, c_mu_jet, alpha_deg):
    clear_pycache()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, COMPARATOR, "--plants", substrate,
         "--c-mu-jet", str(c_mu_jet), "--alpha", str(alpha_deg)],
        capture_output=True, text=True, env=env, cwd=REPO)
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        payload = None
    return dict(rc=proc.returncode, stdout=payload,
                stderr=proc.stderr.strip()[:800])


def main(argv=None):
    ap = argparse.ArgumentParser(description="JF1 section 8.2 fatal-clause control")
    ap.add_argument("--substrate", default=DEFAULT_SUBSTRATE)
    ap.add_argument("--case-id", default="JF1_L1_BLOWN_CMU010_A0")
    ap.add_argument("--c-mu-jet", type=float, default=0.10)
    ap.add_argument("--alpha", type=float, default=0.0)
    ap.add_argument("--workroot", default=None)
    ap.add_argument("--artefact", default=None,
                    help="where to write the preserved plant/mutation record "
                         "(:1733-1735); default artefacts/plant_control_<date>.txt")
    ap.add_argument("--no-artefact", action="store_true")
    args = ap.parse_args(argv)

    workroot = args.workroot or os.path.join(
        os.environ.get("TMPDIR", "/tmp"),
        "jf1_mutation_%s" % datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    if os.path.exists(workroot):
        shutil.rmtree(workroot)
    os.makedirs(workroot)
    try:
        rec = dict(mutation=run_all(args.substrate, args.case_id, workroot),
                   plants=run_plants(args.substrate, args.c_mu_jet, args.alpha))
    finally:
        shutil.rmtree(workroot, ignore_errors=True)

    text = json.dumps(rec, indent=2, default=str)
    sys.stdout.write(text + "\n")
    if not args.no_artefact:
        path = args.artefact or os.path.join(
            ARTEFACT_DIR, "plant_control_%s.txt"
            % datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
        d = os.path.dirname(path)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        open(path, "w").write(text + "\n")
        sys.stderr.write("artefact preserved: %s\n" % path)
    bad = (rec["mutation"].get("verdict") != "GATE REACHED"
           or rec["plants"]["rc"] != 0)
    return 2 if bad else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except HarnessError as exc:
        sys.stderr.write("REFUSED[R-HARNESS]: %s\n" % exc)
        sys.exit(2)
