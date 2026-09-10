#!/usr/bin/env python3
"""SATISFIABILITY SWEEP of every closure completion / admissibility clause.

WHY THIS EXISTS
---------------
`grade_r5d.py:296` carries the clause `n_exec == write_iter`, counting
`ExecutionTime = ... s` lines in `log.frozen`.  The producer,
`kCorrectiveFrozenFoam{,V2}.C`, emits that string at exactly ONE source line,
and that line sits OUTSIDE the outer loop (V1:192, V2:244, both after the
`runTime.writeNow()` at V1:174 / V2:226).  `n_exec` is therefore structurally 1
for every run the solver can ever produce, while `write_iter` is the settle
iteration and is >= 50 by construction.  The clause can never pass.  The
grader's selftest is green only because its fixture
(`grade_r5d.py:_make_complete_case`, ~:416) writes `wi` ExecutionTime lines --
a fixture that disagrees with the live population.

THE TEST THIS SCRIPT APPLIES
----------------------------
"strictly stricter" is not a sufficient check on a guard.  A guard that can
never pass is not strict, it is broken.  Every completion clause must be shown
SATISFIABLE BY THE REAL PRODUCER'S OUTPUT -- not merely green against a
fixture.  For each clause this script asks ONE question and answers it with a
measurement against a NAMED population on disk:

    is there any real artifact on disk that SATISFIES it?

CLASSIFICATION -- three labels, no hedging words:
    SATISFIABLE   (measured, N of M pass, N >= 1)
    UNSATISFIABLE (measured, 0 of M, with the structural reason)
    NOT MEASURED  (no population on disk)

READER CONTROLS
---------------
Every counting reader used below is first shown able to see a NON-ZERO on a
NAMED real artifact, and then shown to FALL to zero when the token is scrubbed
from a copy of that same artifact.  A reader that fails either direction stops
the sweep with rc=2.  A null population is reported as NOT MEASURED and never
as a finding: the first hand-sweep of this defect read `log.run` inside
`r4/frozen/` (the real name is `log.frozen`), examined 0 records, and would
have "confirmed" the defect from a null.

RULES OBSERVED
--------------
* Reads only.  No frozen file is edited; no solver is launched; no verdict is
  moved.  Scrubbed copies are written to a scratch directory only.
* No `assert` carries a guard or a refusal (L-332): refusals are `sys.exit(2)`.
* Green under `python3` and `python3 -O`.
* One NAMED artifact per check; no glob is fed to `tail -1`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile

CLOSURE = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models"
DATA = "/home/ubuntu/closure-data"

# ---------------------------------------------------------------- refusal
def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def load(modname, path):
    """Import a grader by explicit path.  Every grader guards its main()."""
    if not os.path.isfile(path):
        return None
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:                       # import-time failure is a finding
        sys.stderr.write("IMPORT FAILED %s: %s\n" % (path, exc))
        return None
    return mod


# ------------------------------------------------------- named populations
def cases_with(root, logname, depth=1):
    """Sorted case dirs `depth` levels under `root` that carry `logname`.

    BOTH the log NAME and the DEPTH are explicit and never guessed.  The first
    hand-sweep of the R5D defect looked for `log.run` under a tree whose logs
    are `log.frozen` and measured a null; the first draft of THIS script looked
    for `log.solve` one level under `r4/aposteriori`, whose cases sit TWO
    levels down, and measured a second null.  A null is reported as
    NOT MEASURED, never as a finding.
    """
    if not os.path.isdir(root):
        return []
    out = []
    cur = [root]
    for _ in range(depth):
        nxt = []
        for c in cur:
            if os.path.isdir(c):
                nxt.extend(os.path.join(c, n) for n in sorted(os.listdir(c))
                           if os.path.isdir(os.path.join(c, n)))
        cur = nxt
    for d in cur:
        if os.path.isfile(os.path.join(d, logname)):
            out.append(d)
    return sorted(out)


# (root, log name, depth below root).  Every entry was censused on disk before
# it was written here; `rc3` and `rc4` have NO root, by design -- they are
# unfrozen and no compute has run.
POPULATIONS = {
    "R4_FROZEN":      (os.path.join(DATA, "r4", "frozen"), "log.frozen", 1),
    "R5C_FROZEN":     (os.path.join(DATA, "r5c", "frozen"), "log.frozen", 1),
    "R4_APOST":       (os.path.join(DATA, "r4", "aposteriori"), "log.solve", 2),
    "WU_APOST":       (os.path.join(DATA, "aposteriori", "wu2018"), "log.solve", 2),
    "WU_FROZENK":     (os.path.join(DATA, "aposteriori_frozenk", "wu2018"), "log.solve", 2),
    "KAANDORP_APOST": (os.path.join(DATA, "aposteriori", "kaandorp"), "log.run", 1),
    "M1_KOMEGA":      (os.path.join(DATA, "multimodel_sweep", "kOmega"), "log.run", 1),
    "M1_KOSST_NULL":  (os.path.join(DATA, "multimodel_sweep", "kOmegaSST_null"), "log.run", 1),
    "G1_LEVELS":      (os.path.join(DATA, "g1"), "log.run", 1),
    "G2_LEVELS":      (os.path.join(DATA, "g2"), "log.run", 1),
    "RC3_WU":         (os.path.join(DATA, "rc3", "wu2018"), "log.solve", 1),
    "RC4_KAANDORP":   (os.path.join(DATA, "rc4", "kaandorp"), "log.solve", 1),
}


# ------------------------------------------------------- reader controls
EXEC_R5D = re.compile(r"ExecutionTime = [0-9.]+ s")       # grade_r5d.py:293, verbatim
EXEC_ANCHORED = re.compile(r"^ExecutionTime = ", re.M)    # rc3/rc4/g1/g1b, verbatim
TIME_ANCHORED = re.compile(r"^Time = ", re.M)             # rc3/rc4, verbatim


def reader_control(tag, path, rx, token, scratch):
    """Prove `rx` sees a NON-ZERO on the NAMED artifact `path`, and that the
    same reader FALLS TO ZERO when `token` is scrubbed from a copy.  Both
    directions, or the sweep refuses: a zero from a reader not shown able to
    see a non-zero is not evidence."""
    if not os.path.isfile(path):
        return {"tag": tag, "artifact": path, "fired": False,
                "note": "NOT MEASURED: named control artifact absent"}
    txt = open(path, errors="replace").read()
    live = len(rx.findall(txt))
    dst = os.path.join(scratch, tag + ".scrubbed")
    open(dst, "w").write(txt.replace(token, "SCRUBBED_" + tag))
    dead = len(rx.findall(open(dst, errors="replace").read()))
    if live <= 0:
        refuse("reader control %s: %s sees 0 occurrences in the NAMED artifact "
               "%s -- this reader cannot be used to report a zero" % (tag, rx.pattern, path))
    if dead != 0:
        refuse("reader control %s: scrubbed copy still reports %d -- the reader "
               "does not respond to the token it claims to count" % (tag, dead))
    return {"tag": tag, "artifact": path, "fired": True,
            "live_count": live, "scrubbed_count": dead}


def mtime_reader_control(scratch):
    """Prove the age-guard reader (os.path.getmtime strict >) can see BOTH
    directions on two files it made itself."""
    old = os.path.join(scratch, "age_old")
    new = os.path.join(scratch, "age_new")
    open(old, "w").write("old")
    os.utime(old, (1_000_000, 1_000_000))
    open(new, "w").write("new")
    os.utime(new, (2_000_000, 2_000_000))
    fresh = os.path.getmtime(new) > os.path.getmtime(old)
    stale = os.path.getmtime(old) > os.path.getmtime(new)
    if not fresh or stale:
        refuse("mtime reader control: strict-newer comparison did not separate "
               "two files 1e6 s apart (fresh=%r stale=%r)" % (fresh, stale))
    return {"tag": "MTIME", "artifact": scratch, "fired": True,
            "newer_seen": fresh, "older_rejected": (not stale)}


# ------------------------------------------------------------- the sweep
RESULTS = []


def record(clause, instrument, cite, population, npass, ntotal, reason="",
           reader=""):
    if ntotal == 0:
        label = "NOT MEASURED"
    elif npass >= 1:
        label = "SATISFIABLE"
    else:
        label = "UNSATISFIABLE"
    RESULTS.append(dict(clause=clause, instrument=instrument, cite=cite,
                        population=population, n_pass=npass, n_total=ntotal,
                        label=label, reason=reason, reader=reader))


def measure(clause, instrument, cite, popname, predicate, reason_if_zero="",
            reader=""):
    """predicate(case_dir) -> bool.  A predicate that raises is a FAIL for that
    row and the exception text is carried into the reason."""
    root, logname, depth = POPULATIONS[popname]
    pop = cases_with(root, logname, depth)
    npass, errs = 0, []
    for d in pop:
        try:
            if predicate(d):
                npass += 1
        except Exception as exc:
            errs.append("%s: %s" % (os.path.basename(d), exc))
    reason = reason_if_zero if npass == 0 else ""
    if errs:
        reason = (reason + " | predicate raised on %d of %d rows, first: %s"
                  % (len(errs), len(pop), errs[0])).strip(" |")
    record(clause, instrument, "%s  [pop %s = %s/*/%s]" % (cite, popname, root, logname),
           popname, npass, len(pop), reason, reader)
    return npass, len(pop)


def main():
    scratch = tempfile.mkdtemp(prefix="closure_satsweep_")
    controls = []

    # ---- populations census, printed BEFORE any clause verdict
    census = {}
    for name, (root, logname, depth) in POPULATIONS.items():
        census[name] = {"root": root, "log": logname, "depth": depth,
                        "n": len(cases_with(root, logname, depth)),
                        "root_exists": os.path.isdir(root)}

    # ---- reader controls, on NAMED artifacts
    r4_named = os.path.join(DATA, "r4", "frozen", "PHLL10595", "log.frozen")
    solve_named = os.path.join(DATA, "r4", "aposteriori",
                               "PHLL10595", "ceiling", "log.solve")
    run_named = os.path.join(DATA, "multimodel_sweep", "kOmega", "CBFS", "log.run")

    controls.append(reader_control("EXEC_R5D_ON_FROZEN", r4_named, EXEC_R5D,
                                   "ExecutionTime = ", scratch))
    controls.append(reader_control("EXEC_ANCHORED_ON_SOLVE", solve_named,
                                   EXEC_ANCHORED, "ExecutionTime = ", scratch))
    controls.append(reader_control("TIME_ANCHORED_ON_SOLVE", solve_named,
                                   TIME_ANCHORED, "Time = ", scratch))
    controls.append(reader_control("EXEC_ANCHORED_ON_RUN", run_named,
                                   EXEC_ANCHORED, "ExecutionTime", scratch))
    controls.append(mtime_reader_control(scratch))

    # ---- the frozen graders
    R = load("r4_lib", os.path.join(CLOSURE, "R4_sparta_build", "r4_lib.py"))
    if R is None:
        refuse("r4_lib.py did not import; the shared completion helpers cannot "
               "be measured and no clause verdict may be issued")

    g_r5d = load("grade_r5d", os.path.join(
        CLOSURE, "R5D_identity_preserving_completion", "grade_r5d.py"))
    g_m1 = load("grade_m1", os.path.join(
        CLOSURE, "M1_multimodel_sweep", "grade_m1.py"))
    rc3 = load("rc3_ceiling", os.path.join(
        CLOSURE, "RC3_wu_ceiling_gate_validation", "rc3_ceiling.py"))
    rc4 = load("rc4_score", os.path.join(
        CLOSURE, "RC4_kaandorp_propagation_repair", "rc4_score.py"))

    # ================================================================
    # PART 1 -- the frozen-extraction family (log.frozen)
    # ================================================================
    for pop in ("R4_FROZEN", "R5C_FROZEN"):
        measure("frozen_complete: ALL SIX (composite)", "r4_lib.frozen_complete",
                "r4_lib.py:272", pop,
                lambda d: R.frozen_complete(d)[0],
                "every row fails the composite; see the per-clause rows",
                "EXEC/MTIME controls fired")
        measure("frozen_complete c1: rc == 0", "r4_lib.frozen_complete",
                "r4_lib.py:287-292", pop,
                lambda d: open(os.path.join(d, "rc")).read().strip() == "0"
                if os.path.isfile(os.path.join(d, "rc")) else False,
                "no row records rc == 0")
        measure("frozen_complete c2: `End` line in log.frozen",
                "r4_lib.frozen_complete", "r4_lib.py:294-295", pop,
                lambda d: bool(re.search(r"^End\s*$",
                                         open(os.path.join(d, "log.frozen"),
                                              errors="replace").read(), re.M)),
                "no log.frozen carries an End line")
        measure("frozen_complete c3: settle-criterion line present",
                "r4_lib.frozen_complete", "r4_lib.py:298-301", pop,
                lambda d: bool(re.search(r"CONVERGED \(settle criterion\) at iteration (\d+)",
                                         open(os.path.join(d, "log.frozen"),
                                              errors="replace").read())),
                "the solver never emits the settle-criterion line")
        measure("frozen_complete c4: settle verification == SETTLED",
                "r4_lib.frozen_complete", "r4_lib.py:302-309", pop,
                lambda d: (re.search(r"L2\(R\) moved ([0-9.eE+-]+)% .*?\[(SETTLED|NOT SETTLED)\]",
                                     open(os.path.join(d, "log.frozen"),
                                          errors="replace").read(), re.S) or [None, None, None])[2] == "SETTLED"
                if re.search(r"L2\(R\) moved ([0-9.eE+-]+)% .*?\[(SETTLED|NOT SETTLED)\]",
                             open(os.path.join(d, "log.frozen"), errors="replace").read(), re.S)
                else False,
                "no row reports SETTLED")
        measure("frozen_complete c5: zero `bounding omega` before the write",
                "r4_lib.frozen_complete", "r4_lib.py:316-322", pop,
                lambda d: _bounding_before_write(d) == 0,
                "every row bounds omega before the write (clipped, not settled)")
        measure("frozen_complete c6: last time dir == solver write iteration",
                "r4_lib.frozen_complete", "r4_lib.py:323-328", pop,
                lambda d: _last_time_eq_write_iter(d),
                "the last time dir never equals the write iteration")
        measure("frozen_complete c7: 8 fields present AND newer than 0/",
                "r4_lib.frozen_complete", "r4_lib.py:329-340", pop,
                lambda d: _fields_ok(d),
                "no row has all eight fields newer than 0/",
                "MTIME control fired")

    # ---- THE DEFECT
    if g_r5d is not None:
        for pop in ("R4_FROZEN", "R5C_FROZEN"):
            measure("R5D clause 5: n_exec == write_iter",
                    "grade_r5d.completion_rule4", "grade_r5d.py:293-300", pop,
                    lambda d: _r5d_exec_clause(d),
                    "kCorrectiveFrozenFoam{,V2}.C emits `ExecutionTime = ` at ONE "
                    "source line, OUTSIDE the outer loop (V1:192, V2:244, both "
                    "after runTime.writeNow() at V1:174/V2:226), so n_exec == 1 "
                    "for every producible run, while write_iter is the settle "
                    "iteration and is >= 50 by construction",
                    "EXEC_R5D_ON_FROZEN control fired")
            measure("R5D composite: completion_rule4 overall",
                    "grade_r5d.completion_rule4", "grade_r5d.py:276-302", pop,
                    lambda d: g_r5d.completion_rule4(d)[0],
                    "the clause-5 row above is the sole reason",
                    "EXEC_R5D_ON_FROZEN control fired")

    # ================================================================
    # PART 1 -- the simpleFoam propagation family (log.solve)
    # ================================================================
    for pop in ("R4_APOST", "WU_APOST", "WU_FROZENK"):
        measure("solve_complete: composite (no exec-count clause)",
                "r4_lib.solve_complete", "r4_lib.py:494", pop,
                lambda d: R.solve_complete(d)[0],
                "every row fails the composite",
                "EXEC/TIME/MTIME controls fired")
        measure("solve_complete: last time dir == last solver iteration",
                "r4_lib.solve_complete", "r4_lib.py:532-536", pop,
                lambda d: _solve_lastdir_eq_lastiter(d),
                "the last time dir never equals the last solver iteration")
        # the RC3/RC4 clause-5 formulation, measured on the SAME producer
        measure("RC3/RC4 clause 5: n_exec == n_time (log.solve)",
                "rc3_ceiling.completion / rc4_score.completion",
                "rc3_ceiling.py:253-263, rc4_score.py:235-241", pop,
                lambda d: _exec_eq_time(d, "log.solve"),
                "simpleFoam does not emit one ExecutionTime line per Time line",
                "EXEC_ANCHORED_ON_SOLVE + TIME_ANCHORED_ON_SOLVE controls fired")

    # ================================================================
    # PART 1 -- the M1 / G1 sweep family (log.run)
    # ================================================================
    if g_m1 is not None:
        cap = getattr(g_m1, "CAP_ITER", None)
        for pop in ("M1_KOMEGA", "M1_KOSST_NULL"):
            measure("M1 clause: exec_count == CAP_ITER (%s)" % cap,
                    "grade_m1.completion", "grade_m1.py:316", pop,
                    lambda d: _exec_count_eq(d, "log.run", cap),
                    "no log.run carries exactly CAP_ITER ExecutionTime lines",
                    "EXEC_ANCHORED_ON_RUN control fired")
            measure("M1 clause: last_time == CAP_ITER", "grade_m1.completion",
                    "grade_m1.py:310-313", pop,
                    lambda d: _last_time_line_eq(d, "log.run", cap),
                    "no log.run's last Time line equals CAP_ITER")
            measure("M1 clause: physics fields present at CAP_ITER",
                    "grade_m1.completion", "grade_m1.py:314-315", pop,
                    lambda d: all(os.path.isfile(os.path.join(d, str(cap), f))
                                  for f in g_m1.PHYSICS_FIELDS),
                    "no row has all physics fields at the cap iteration")
            measure("M1 clause: age guard vs 0/%s" % getattr(g_m1, "AGE_DATUM", "?"),
                    "grade_m1.completion", "grade_m1.py:317-322", pop,
                    lambda d: _m1_age(d, g_m1, cap),
                    "no row's cap fields are newer than the 0/ datum",
                    "MTIME control fired")
            measure("M1 composite: completion() complete",
                    "grade_m1.completion", "grade_m1.py:305-344", pop,
                    lambda d: g_m1.completion(
                        d, g_m1.parse_log(os.path.join(d, "log.run")))["complete"],
                    "no row is complete under M1's own composite")

    # ---- G1 / G2 grid triples: the populations are per-level, named explicitly
    for tag in ("G1", "G2"):
        measure("%s P7: ExecutionTime lines == registered endTime" % tag,
                "grade_g1.completion / grade_g2.completion",
                "grade_g1.py:501-505, grade_g2.py:710-715", "%s_LEVELS" % tag,
                lambda d: _exec_count_eq_endtime_from_controldict(d),
                "no level's ExecutionTime count equals its controlDict endTime",
                "EXEC_ANCHORED_ON_RUN control fired")
        measure("%s P4: last time dir == registered endTime" % tag,
                "grade_g1.completion / grade_g2.completion",
                "grade_g1.py:478-483", "%s_LEVELS" % tag,
                lambda d: _lastdir_eq_endtime(d),
                "no level's last time dir equals its controlDict endTime")

    # ================================================================
    # PART 2 -- RC3 and RC4, BEFORE the freeze
    # ================================================================
    for tag, mod, pop in (("RC3", rc3, "RC3_WU"), ("RC4", rc4, "RC4_KAANDORP")):
        if mod is None:
            continue
        req = getattr(mod, "B").REQUIRED_FIELDS
        measure("%s clause 4: REQUIRED_FIELDS %s present at last time"
                % (tag, ",".join(req)), "%s.completion" % tag.lower(),
                "rc3_ceiling.py:245-250 / rc4_score.py:227-234", pop,
                lambda d, r=req: all(os.path.exists(os.path.join(
                    d, R.latest_time(d), f)) for f in r),
                "no row on the RC population carries every required field")
        measure("%s clause 5: n_exec == n_time" % tag, "%s.completion" % tag.lower(),
                "rc3_ceiling.py:253-263 / rc4_score.py:235-241", pop,
                lambda d: _exec_eq_time(d, "log.solve"),
                "the producer does not emit one ExecutionTime per Time",
                "EXEC/TIME controls fired")
        measure("%s clause 6: age guard vs 0/U" % tag, "%s.completion" % tag.lower(),
                "rc3_ceiling.py:265-278 / rc4_score.py:242-249", pop,
                lambda d, r=req: _rc_age(d, r),
                "no row's fields are newer than 0/U", "MTIME control fired")
        measure("%s composite: completion()" % tag, "%s.completion" % tag.lower(),
                "rc3_ceiling.py:223 / rc4_score.py:207", pop,
                lambda d, m=mod: m.completion(d)[0],
                "no row is complete under the RC composite")

    out = {"census": census, "reader_controls": controls, "clauses": RESULTS}
    print(json.dumps(out, indent=2, sort_keys=False))

    # a compact table on stderr so the JSON stays machine-clean
    sys.stderr.write("\n%-62s %-14s %s\n" % ("CLAUSE", "LABEL", "N/M"))
    for r in RESULTS:
        sys.stderr.write("%-62s %-14s %d/%d\n" % (r["clause"][:62], r["label"],
                                                  r["n_pass"], r["n_total"]))
    shutil.rmtree(scratch, ignore_errors=True)
    return 0


# ------------------------------------------------------------- predicates
def _read(d, logname):
    return open(os.path.join(d, logname), errors="replace").read()


def _bounding_before_write(d):
    txt = _read(d, "log.frozen")
    pre = txt[:txt.index("Writing fields")] if "Writing fields" in txt else txt
    return pre.count("bounding omega")


def _write_iter(d):
    m = re.search(r"Writing fields at iteration (\d+)", _read(d, "log.frozen"))
    return int(m.group(1)) if m else None


def _last_time_eq_write_iter(d):
    import r4_lib as R
    wi = _write_iter(d)
    if wi is None:
        return False
    return float(R.latest_time(d)) == float(wi)


def _fields_ok(d):
    import r4_lib as R
    lt = R.latest_time(d)
    tdir, zero = os.path.join(d, lt), os.path.join(d, "0")
    for f in ("U", "k", "omega", "nut", "bijDelta", "kDeficit", "bijData",
              "grad(U)"):
        fp = os.path.join(tdir, f)
        if not os.path.exists(fp):
            return False
        zp = os.path.join(zero, f)
        if os.path.exists(zp) and os.path.getmtime(fp) <= os.path.getmtime(zp):
            return False
    return True


def _r5d_exec_clause(d):
    """grade_r5d.py:293-296 verbatim, isolated from the six conditions above it."""
    n_exec = len(EXEC_R5D.findall(_read(d, "log.frozen")))
    wi = _write_iter(d)
    return wi is not None and n_exec == wi


def _exec_eq_time(d, logname):
    txt = _read(d, logname)
    return len(EXEC_ANCHORED.findall(txt)) == len(TIME_ANCHORED.findall(txt))


def _exec_count_eq(d, logname, target):
    if target is None:
        return False
    return len(EXEC_ANCHORED.findall(_read(d, logname))) == int(target)


def _last_time_line_eq(d, logname, target):
    if target is None:
        return False
    times = re.findall(r"^Time = ([0-9.eE+-]+)", _read(d, logname), re.M)
    if not times:
        return False
    return abs(float(times[-1]) - float(target)) < 1e-9


def _m1_age(d, g_m1, cap):
    zero_datum = os.path.join(d, "0", g_m1.AGE_DATUM)
    end_dir = os.path.join(d, str(cap))
    if not os.path.isfile(zero_datum):
        return False
    t0 = os.path.getmtime(zero_datum)
    for f in g_m1.PHYSICS_FIELDS:
        fp = os.path.join(end_dir, f)
        if not os.path.isfile(fp) or os.path.getmtime(fp) <= t0:
            return False
    return True


def _endtime_of(d):
    cd = os.path.join(d, "system", "controlDict")
    if not os.path.isfile(cd):
        return None
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+);", open(cd, errors="replace").read(), re.M)
    return float(m.group(1)) if m else None


def _exec_count_eq_endtime_from_controldict(d):
    et = _endtime_of(d)
    if et is None:
        return False
    return len(EXEC_ANCHORED.findall(_read(d, "log.run"))) == int(et)


def _lastdir_eq_endtime(d):
    import r4_lib as R
    et = _endtime_of(d)
    if et is None:
        return False
    return float(R.latest_time(d)) == et


def _solve_lastdir_eq_lastiter(d):
    import r4_lib as R
    times = re.findall(r"^Time = (\d+)", _read(d, "log.solve"), re.M)
    if not times:
        return False
    return float(R.latest_time(d)) == float(int(times[-1]))


def _rc_age(d, req):
    import r4_lib as R
    zu = os.path.join(d, "0", "U")
    if not os.path.exists(zu):
        return False
    t0 = os.path.getmtime(zu)
    lt = R.latest_time(d)
    for f in req:
        fp = os.path.join(d, lt, f)
        if not os.path.exists(fp) or os.path.getmtime(fp) <= t0:
            return False
    return True


if __name__ == "__main__":
    sys.exit(main())
