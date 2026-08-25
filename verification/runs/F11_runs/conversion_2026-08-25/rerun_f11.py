#!/usr/bin/env python3
"""
F11 CONVERSION -- the launcher, frozen with the pre-registration.

Drives the six solves of section 6 of
``verification/campaign/F11_CONVERSION_PREREGISTRATION.md`` (committed
157793db5ff6bbdda7ab22299abe5725d96e9b37) into FRESH case directories under
``conversion_2026-08-25/runs/<rung>/<level>/``.

``verification/runs/F11_runs/cavity_ladder.py`` is used BYTE-UNCHANGED as the
case generator (section 6), and this file verifies that before it builds
anything.  It adds only the three artifacts the completion rule needs and that
module does not write -- ``meta.json``, ``run_rc.txt`` and
``launch_timing.json`` -- plus the ONE registered change to the case
dictionaries in section 6.1, applied with an assert and never blind.

SECTION 6.1 AS AMENDED 2026-08-25, PRE-COMPUTE, ARM B.  The frozen section 6.1
moved the ``centerlineProfiles`` object itself onto ``timeStep`` / 250.  A
mechanism probe measured that this arrangement CANNOT SATISFY THE FROZEN
CLAUSE C4: ``simpleFoam`` stops early under ``residualControl``, the ``sets``
object writes only at multiples of 250, and NOTHING is written at the
convergence iteration -- so ``centerlineProfiles/<N>/`` never exists and C4
fails by construction on every run.  What this launcher now writes instead:

  * ``centerlineProfiles`` STAYS at ``onEnd``, so both ``.xy`` files land under
    ``centerlineProfiles/<N>/`` at the CONVERGED iteration -- the frozen
    literal path C4 names, unchanged;
  * a SEPARATELY NAMED ``centerlineSeries`` object, sampling THE SAME POINTS,
    is added at ``timeStep`` / ``250``, and is what the plateau's earlier
    samples are read from (``grade_f11.py``).

This alters NO gate, NO threshold, NO cap and NO label.  It changes only how
the artifact is produced, restoring the path the freeze already names.  The
arrangement actually written is RE-READ FROM DISK and asserted; the launcher
REFUSES rather than degrade if what it wrote is not what it intended.

BUDGET (CLAUDE.md rule 12; section 7).  The cap is HARD: **13.0 core-minutes =
780 core-seconds**.  AN OVERRUN STOPS THE RUN; IT DOES NOT GET A NEW BUDGET.
Three enforcement points, all here:

  1. a per-run wall cap of ``max(60 s, 2.5 x predicted)`` -- 60 / 60 / 442 for
     the Re 1000 ladder and 60 / 60 / 674 for Re 100.  A run past its cap is
     SIGTERMed and recorded ``KILLED``, which fails C1/C2 and therefore grades
     its ladders NOT A RESULT -- never a softened number;
  2. a pre-wave budget check -- a wave whose predicted cost does not fit the
     remaining budget with 20 % headroom is NOT LAUNCHED and its ladders grade
     PENDING;
  3. a GLOBAL WATCHDOG polling every 5 s that terminates every live run the
     moment cumulative core-seconds reach 780.  **This is the binding
     enforcement**: the per-run caps sum ABOVE the budget, so the per-run caps
     alone do not enforce it.

     A DEFECT IN THE FROZEN DOCUMENT, recorded here and NOT repaired: section 7
     states that sum as "1,296 s (21.6 core-min)".  The six caps that same
     paragraph registers -- 60, 60, 442, 60, 60, 674 -- sum to 1,355.575 s
     (22.59 core-min).  The arithmetic is wrong by 59.575 s.  It is IMMATERIAL
     to the clause's conclusion, which is that the caps sum above the 780 s
     budget so the watchdog binds; that holds a fortiori at the larger figure.
     The caps implemented below are the six the document registers, unchanged.
     Surfaced by grade_f11.py --selftest, which carries it as a live check.

THE GUARD (CLAUDE.md rule 4).  A child REFUSES (rc = 3) any case directory that
already exists, and separately refuses one carrying a ``0/`` or a time
directory.  No run in this conversion can inherit a ``0/``, a time directory or
a ``postProcessing/`` tree from the 2026-07-30 campaign or from a retry.

WHAT THIS FILE NEVER TOUCHES.  It signals only processes it started itself.
Other teams' solvers on this box are never inspected for a kill and never
signalled, and this launcher writes nothing outside
``verification/runs/F11_runs/conversion_2026-08-25/``.

Per-run wall seconds and rank count are written to ``launch_timing.json`` in
every case directory so that core-minutes are computable FROM LOGS afterwards
for the mandatory ``docs/COST_CALIBRATION.md`` row (section 7).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
F11_ROOT = os.path.dirname(HERE)                  # verification/runs/F11_runs
REPO = os.path.dirname(os.path.dirname(os.path.dirname(F11_ROOT)))
RUNS = os.path.join(HERE, "runs")
sys.path.insert(0, F11_ROOT)

FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---------------------------------------------------------------------------
# FROZEN -- transcribed from the pre-registration, not chosen here
# ---------------------------------------------------------------------------

# section 6: the run matrix.  (level name, n, cells, endTime)
LEVELS = (
    ("coarse", 32, 1024, 4000),
    ("medium", 64, 4096, 4000),
    ("fine", 128, 16384, 9000),
)
RUNGS = ("re1000", "re100")
RE_OF = {"re100": 100.0, "re1000": 1000.0}
GRADING_RATIO = 8.0            # section 4.1: held at 8.0 on EVERY level, so
                               # the mesh family is geometrically self-similar

# section 7: predicted core-seconds, per run.  cost_basis is in the
# pre-registration; the n = 32 rows are labelled ESTIMATE there and the rest
# are measured from named logs.
PRED = {
    ("re1000", "coarse"): 4.0,       # ESTIMATE, labelled (no n = 32 exists)
    ("re1000", "medium"): 14.39,     # measured
    ("re1000", "fine"): 176.73,      # measured
    ("re100", "coarse"): 4.0,        # ESTIMATE, labelled
    ("re100", "medium"): 12.58,      # measured
    ("re100", "fine"): 269.50,       # measured rate x measured iteration count
}
COST_BASIS = {
    ("re1000", "coarse"): "ESTIMATE, labelled -- no n = 32 measurement exists",
    ("re1000", "medium"): "measured, f11_re1000_n64_20260730T041833Z.log",
    ("re1000", "fine"): "measured, f11_re1000_n128_20260730T041833Z.log",
    ("re100", "coarse"): "ESTIMATE, labelled -- no n = 32 measurement exists",
    ("re100", "medium"): "measured, f11_re100_n64_20260730T041833Z.log",
    ("re100", "fine"): "measured rate x measured iteration count, "
                       "f11_re100_n128_20260730T041833Z.log",
}

# section 7: the cap and its enforcement
CAP_CORE_MIN = 13.0
CAP_CORE_S = 780.0
WATCHDOG_POLL_S = 5.0
WAVE_HEADROOM = 1.20           # "with 20 % headroom"
MAX_CONCURRENT = 2             # "At most 2 live runs, deliberately below the
                               # box's core count"

# section 7: launch order, FROZEN.  If the budget stops the line, wave 4 is
# lost first and the three Re 100 ladders grade PENDING -- a triple is never
# left half-built: losing a wave loses a whole rung, never one level.
WAVES = (
    (("re1000", "coarse"), ("re1000", "medium")),
    (("re1000", "fine"),),
    (("re100", "coarse"), ("re100", "medium")),
    (("re100", "fine"),),
)

# section 6: the generator is used BYTE-UNCHANGED.
CAVITY_LADDER_REL = "verification/runs/F11_runs/cavity_ladder.py"
CAVITY_LADDER_BLOB = "e9381a6e140c2e182c1f32c6c350b38d9f3db597"

RANKS = 1                      # section 7: "All runs are serial, 1 rank"

RC_OK, RC_FAIL, RC_REFUSE_EXISTS, RC_KILLED = 0, 1, 3, 143


def wall_cap(key):
    """Section 7 enforcement point 1: max(60 s, 2.5 x predicted).  Reproduces
    the frozen 60 / 60 / 442 / 60 / 60 / 674 -- asserted in
    grade_f11.py --selftest, not merely claimed here."""
    return max(60.0, 2.5 * PRED[key])


def case_dir(key):
    return os.path.join(RUNS, key[0], key[1])


def level_spec(level):
    for name, n, cells, cap in LEVELS:
        if name == level:
            return n, cells, cap
    raise KeyError(level)


# ---------------------------------------------------------------------------
# the generator freeze
# ---------------------------------------------------------------------------

def verify_generator():
    path = os.path.join(REPO, CAVITY_LADDER_REL)
    with open(path, "rb") as fh:
        data = fh.read()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    got = h.hexdigest()
    if got != CAVITY_LADDER_BLOB:
        sys.stderr.write(
            "REFUSED: section 6 uses %s BYTE-UNCHANGED as the case generator, "
            "and it is not byte-unchanged.\n  frozen  %s\n  on disk %s\n"
            % (CAVITY_LADDER_REL, CAVITY_LADDER_BLOB, got))
        return None
    return got


# ---------------------------------------------------------------------------
# section 6.1 -- the ONE registered change to the case dictionaries
#                AS AMENDED 2026-08-25, PRE-COMPUTE: ARM B
# ---------------------------------------------------------------------------

PROFILES_OBJECT = "centerlineProfiles"   # GRADED artifact; stays at onEnd, so
                                         # it lands at the CONVERGED iteration
SERIES_OBJECT = "centerlineSeries"       # PERIODIC series; timeStep / 250
SERIES_INTERVAL = 250                    # section 6.1's registered interval


def find_block(txt, name):
    """Locate the OpenFOAM sub-dictionary ``name { ... }`` by BRACE COUNTING,
    never by a regex over nested braces.

    Returns ``(start, end, n_found)``.  ``start`` indexes the first character
    of the name and ``end`` is one past its closing brace.  When ``n_found``
    is not 1 both indices are ``None`` -- the caller decides what a wrong count
    means, and no caller here treats it as anything but a refusal.
    """
    hits = list(re.finditer(r"^([ \t]*)%s[ \t]*$" % re.escape(name), txt,
                            re.M))
    if len(hits) != 1:
        return None, None, len(hits)
    m = hits[0]
    try:
        i = txt.index("{", m.end())
    except ValueError:
        return None, None, 1
    depth, j = 0, i
    while j < len(txt):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                return m.start(), j + 1, 1
        j += 1
    return None, None, 1


def sets_body(block):
    """The ``sets { ... }`` sub-dictionary of one function object, so that the
    two objects can be proved to sample THE SAME POINTS.  If the plateau were
    measured at a different station from the graded value the whole
    arrangement would be worthless, and that is a thing to assert, not to
    assume."""
    s, e, n = find_block(block, "sets")
    if n != 1 or s is None:
        return None
    return block[s:e]


def build_series_block(profiles_block):
    """Arm B's periodic object, built FROM the graded object so the two sample
    the same points by construction, with only the name and the two controls
    changed."""
    blk, n = re.subn(r"^([ \t]*)%s[ \t]*$" % re.escape(PROFILES_OBJECT),
                     lambda m: m.group(1) + SERIES_OBJECT, profiles_block,
                     count=1, flags=re.M)
    if n != 1:
        raise RuntimeError("section 6.1 (arm B): could not rename the copied "
                           "sampling object exactly once (renamed %d)" % n)
    blk, n = re.subn(
        r"^([ \t]*)executeControl(\s+)onEnd;[ \t]*$",
        lambda m: ("%sexecuteControl%stimeStep;\n%sexecuteInterval%s%d;"
                   % (m.group(1), m.group(2), m.group(1), m.group(2),
                      SERIES_INTERVAL)), blk, flags=re.M)
    if n != 1:
        raise RuntimeError("section 6.1 (arm B): expected exactly ONE "
                           "'executeControl onEnd;' in the copied object, "
                           "found %d" % n)
    blk, n = re.subn(
        r"^([ \t]*)writeControl(\s+)onEnd;[ \t]*$",
        lambda m: ("%swriteControl%stimeStep;\n%swriteInterval%s%d;"
                   % (m.group(1), m.group(2), m.group(1), m.group(2),
                      SERIES_INTERVAL)), blk, flags=re.M)
    if n != 1:
        raise RuntimeError("section 6.1 (arm B): expected exactly ONE "
                           "'writeControl onEnd;' in the copied object, "
                           "found %d" % n)
    return blk


def assert_arm_b_arrangement(txt, end_time, where="<memory>"):
    """REFUSE unless the dictionary is EXACTLY arm B's arrangement.

    This is the assertion the launcher makes on WHAT IT ACTUALLY WROTE,
    re-read from disk -- not on the string it meant to write.  It is also the
    mutation surface ``--selftest`` attacks: a dictionary whose two sampling
    objects have been COLLAPSED BACK INTO ONE fails here, and catching that is
    the entire reason this function exists.

    Returns a dict describing the arrangement it verified.
    """
    if int(end_time) == SERIES_INTERVAL:
        raise RuntimeError(
            "section 6.1 (arm B): endTime equals the sampling interval %d, so "
            "the interval counts below could not distinguish the top-level "
            "field write from the sampling write; refusing rather than "
            "asserting something that cannot discriminate" % SERIES_INTERVAL)

    ps, pe, n_prof = find_block(txt, PROFILES_OBJECT)
    ss, se, n_ser = find_block(txt, SERIES_OBJECT)
    if n_prof != 1:
        raise RuntimeError(
            "section 6.1 (arm B): expected exactly ONE '%s' function object in "
            "%s, found %d.  That object is the GRADED artifact and the frozen "
            "completion clause C4 names its literal path "
            "postProcessing/centerlineProfiles/<N>/."
            % (PROFILES_OBJECT, where, n_prof))
    if n_ser != 1:
        raise RuntimeError(
            "section 6.1 (arm B): expected exactly ONE '%s' function object in "
            "%s, found %d.  THE TWO SAMPLING OBJECTS MUST NOT BE COLLAPSED "
            "INTO ONE: a single object on timeStep/%d writes nothing at the "
            "early residualControl stop, so centerlineProfiles/<N>/ never "
            "exists and C4 fails by construction; a single object on onEnd "
            "writes no periodic series, so the plateau is UNMEASURED.  Arm B "
            "needs BOTH." % (SERIES_OBJECT, where, n_ser, SERIES_INTERVAL))
    pb, sb = txt[ps:pe], txt[ss:se]

    # -- the GRADED object stays at onEnd: that is what puts the .xy under the
    #    CONVERGED iteration and satisfies C4 WITHOUT CHANGING C4.
    for key in ("executeControl", "writeControl"):
        if len(re.findall(r"^\s*%s\s+onEnd;\s*$" % key, pb, re.M)) != 1:
            raise RuntimeError(
                "section 6.1 (arm B): '%s' must carry exactly one '%s onEnd;' "
                "in %s.  Moving the graded object off onEnd is precisely the "
                "defect this amendment repairs: it would write only at "
                "multiples of %d and nothing at the convergence iteration."
                % (PROFILES_OBJECT, key, where, SERIES_INTERVAL))
    if re.search(r"^\s*(?:execute|write)Interval\b", pb, re.M):
        raise RuntimeError(
            "section 6.1 (arm B): the graded '%s' object in %s carries a "
            "periodic interval; it must be onEnd only" % (PROFILES_OBJECT,
                                                          where))

    # -- the PERIODIC object is timeStep / 250 and carries no onEnd.
    for key in ("executeControl", "writeControl"):
        if len(re.findall(r"^\s*%s\s+timeStep;\s*$" % key, sb, re.M)) != 1:
            raise RuntimeError(
                "section 6.1 (arm B): '%s' must carry exactly one '%s "
                "timeStep;' in %s" % (SERIES_OBJECT, key, where))
    for key in ("executeInterval", "writeInterval"):
        if len(re.findall(r"^\s*%s\s+%d;\s*$" % (key, SERIES_INTERVAL), sb,
                          re.M)) != 1:
            raise RuntimeError(
                "section 6.1 (arm B): '%s' must carry exactly one '%s %d;' in "
                "%s" % (SERIES_OBJECT, key, SERIES_INTERVAL, where))
    if "onEnd" in sb:
        raise RuntimeError("section 6.1 (arm B): an 'onEnd' control survived "
                           "in the periodic '%s' object in %s"
                           % (SERIES_OBJECT, where))

    # -- the two objects sample THE SAME POINTS.  Otherwise the plateau would
    #    be measured at a different station from the graded value.
    p_sets, s_sets = sets_body(pb), sets_body(sb)
    if p_sets is None or s_sets is None:
        raise RuntimeError("section 6.1 (arm B): could not locate a single "
                           "'sets' sub-dictionary in each sampling object in "
                           "%s" % where)
    if p_sets != s_sets:
        raise RuntimeError(
            "section 6.1 (arm B): '%s' and '%s' in %s do not sample the same "
            "points.  The plateau would then be measured at a different "
            "station from the graded value, which is worse than not measuring "
            "it." % (PROFILES_OBJECT, SERIES_OBJECT, where))

    # -- FIELD WRITES UNTOUCHED, asserted and not assumed.
    if len(re.findall(r"^\s*writeInterval\s+%d;\s*$" % end_time, txt,
                      re.M)) != 1:
        raise RuntimeError("section 6.1 must leave the top-level "
                           "'writeInterval %d;' intact in %s and it did not"
                           % (end_time, where))
    if len(re.findall(r"^\s*purgeWrite\s+1;\s*$", txt, re.M)) != 1:
        raise RuntimeError("section 6.1 must leave 'purgeWrite 1;' intact in "
                           "%s" % where)
    if len(re.findall(r"^\s*endTime\s+%d;\s*$" % end_time, txt, re.M)) != 1:
        raise RuntimeError("the endTime in %s is not the section 6 value %d"
                           % (where, end_time))

    # -- and the counting arguments, over the WHOLE dictionary, so a stray
    #    third copy of anything is caught rather than hidden by the two block
    #    reads above.
    counts = dict(
        onEnd=txt.count("onEnd"),
        type_sets=len(re.findall(r"^\s*type\s+sets;\s*$", txt, re.M)),
        writeInterval_250=len(re.findall(r"^\s*writeInterval\s+%d;\s*$"
                                         % SERIES_INTERVAL, txt, re.M)),
        executeInterval_250=len(re.findall(r"^\s*executeInterval\s+%d;\s*$"
                                           % SERIES_INTERVAL, txt, re.M)),
        writeControl_timeStep=len(re.findall(
            r"^\s*writeControl\s+timeStep;\s*$", txt, re.M)))
    want = dict(onEnd=2, type_sets=2, writeInterval_250=1,
                executeInterval_250=1, writeControl_timeStep=2)
    if counts != want:
        raise RuntimeError(
            "section 6.1 (arm B): the dictionary in %s does not have arm B's "
            "shape.  expected %r, found %r.  (onEnd twice: executeControl and "
            "writeControl of the graded object.  type sets twice: the two "
            "sampling objects.  writeControl timeStep twice: the top-level "
            "field write and the periodic series.)" % (where, want, counts))
    if txt.count("onEnd") != pb.count("onEnd"):
        raise RuntimeError("section 6.1 (arm B): an 'onEnd' control lives "
                           "outside the graded '%s' object in %s"
                           % (PROFILES_OBJECT, where))
    return dict(section="6.1", amendment="2026-08-25 PRE-COMPUTE, arm B",
                graded_object=PROFILES_OBJECT,
                graded_executeControl="onEnd", graded_writeControl="onEnd",
                series_object=SERIES_OBJECT,
                series_executeControl="timeStep",
                series_executeInterval=SERIES_INTERVAL,
                series_writeControl="timeStep",
                series_writeInterval=SERIES_INTERVAL,
                same_points=True, field_writes_untouched=True,
                endTime=end_time, counts=counts)


def apply_section_6_1(case, end_time):
    """Section 6.1 AS AMENDED 2026-08-25 (pre-compute, arm B).

    The generator emits ONE sampling object, ``centerlineProfiles``, carrying
    ``executeControl onEnd; writeControl onEnd;`` -- one sample set per run,
    from which no plateau can be measured.  The frozen section 6.1 moved THAT
    object onto ``timeStep`` / 250; a mechanism probe measured that doing so
    writes nothing at the early ``residualControl`` stop, so
    ``centerlineProfiles/<N>/`` never exists and the frozen clause C4 fails by
    construction on every run.

    What is written instead:

      * ``centerlineProfiles`` is LEFT at ``onEnd`` -- the graded ``.xy`` files
        land under ``centerlineProfiles/<N>/`` at the CONVERGED iteration, the
        frozen literal path, unchanged;
      * a separately named ``centerlineSeries`` object sampling THE SAME
        POINTS is inserted at ``executeControl timeStep; executeInterval 250;
        writeControl timeStep; writeInterval 250``, and is what the plateau's
        earlier samples are read from.

    FIELD WRITES ARE UNTOUCHED: ``controlDict``'s top-level ``writeControl
    timeStep; writeInterval <endTime>; purgeWrite 1`` is asserted intact
    afterwards, so this adds no field I/O.  It changes WHEN a sample is
    written, never WHAT the converged field is -- and the probe measured that
    too: arm A and arm B both converged at 747 iterations at Re 1000, n = 32.

    Inserted with an assert, never blind (CLAUDE.md rule 14's discipline), and
    the arrangement is asserted TWICE: once on the text about to be written and
    once on the text RE-READ FROM DISK.  It REFUSES rather than degrade if the
    dictionary it wrote is not the one it intended.
    """
    path = os.path.join(case, "system", "controlDict")
    txt = open(path).read()

    ps, pe, n_prof = find_block(txt, PROFILES_OBJECT)
    if n_prof != 1:
        raise RuntimeError(
            "section 6.1: expected exactly ONE '%s' function object in %s, "
            "found %d -- refusing to edit a dictionary that is not the one the "
            "pre-registration describes" % (PROFILES_OBJECT, path, n_prof))
    _, _, n_ser = find_block(txt, SERIES_OBJECT)
    if n_ser != 0:
        raise RuntimeError(
            "section 6.1: '%s' already exists in %s (found %d); this launcher "
            "always builds into a FRESH case and refuses to edit a dictionary "
            "it has already edited" % (SERIES_OBJECT, path, n_ser))

    profiles_block = txt[ps:pe]
    series_block = build_series_block(profiles_block)
    indent = re.match(r"[ \t]*", profiles_block).group(0)
    new_txt = txt[:pe] + "\n\n" + indent + series_block.lstrip() + txt[pe:]

    # assert on what is ABOUT to be written ...
    assert_arm_b_arrangement(new_txt, end_time, where="<in memory, %s>" % path)
    open(path, "w").write(new_txt)
    # ... and again on what IS on disk.  A launcher that trusts its own string
    # has not checked anything (CLAUDE.md rule 3's discipline, applied to a
    # dictionary rather than to a number).
    meta = assert_arm_b_arrangement(open(path).read(), end_time, where=path)
    meta["controlDict"] = path
    return meta


# ---------------------------------------------------------------------------
# child: one run
# ---------------------------------------------------------------------------

_LIVE = {"proc": None, "case": None, "t0": None}


def _sigterm(signum, frame):
    """SIGTERMed by the watchdog or by a per-run wall cap.  Kill the solver,
    record a NON-ZERO rc so the run fails C1, record the timing so the wall
    seconds spent are still costed, and exit.  A killed run is never softened
    into a number."""
    p = _LIVE.get("proc")
    if p is not None and p.poll() is None:
        try:
            p.send_signal(signal.SIGTERM)
            p.wait(timeout=20)
        except Exception:                                      # noqa: BLE001
            try:
                p.kill()
            except Exception:                                  # noqa: BLE001
                pass
    case = _LIVE.get("case")
    if case and os.path.isdir(case):
        open(os.path.join(case, "run_rc.txt"), "w").write("%d\n" % RC_KILLED)
        json.dump(dict(wall_s=time.time() - (_LIVE.get("t0") or time.time()),
                       ranks=RANKS, killed=True,
                       killed_reason="SIGTERM -- budget cap or per-run wall "
                                     "cap; an overrun stops the run and does "
                                     "not get a new budget"),
                  open(os.path.join(case, "launch_timing.json"), "w"),
                  indent=2)
    sys.exit(RC_KILLED)


def sh(cmd, cwd, logfile):
    """Run one OpenFOAM utility, keeping its log.  Registered as its own
    subprocess so the SIGTERM handler can reach it."""
    full = "source %s >/dev/null 2>&1; %s" % (FOAM_BASHRC, cmd)
    p = subprocess.Popen(["bash", "-c", full], cwd=cwd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    _LIVE["proc"] = p
    out, _ = p.communicate()
    _LIVE["proc"] = None
    with open(logfile, "wb") as fh:
        fh.write(out)
    return p.returncode


def run_one_child(rung, level):
    key = (rung, level)
    cd = case_dir(key)
    _LIVE["case"], _LIVE["t0"] = cd, time.time()

    # ---- THE GUARD (CLAUDE.md rule 4; section 5) --------------------------
    if os.path.exists(cd):
        sys.stderr.write(
            "REFUSED: %s already exists. The completion rule's guard refuses a "
            "case where 0/ or a time directory already exists, and this "
            "conversion always runs into a FRESH directory -- it never "
            "inherits a 0/, a time directory or a postProcessing/ tree from "
            "the 2026-07-30 campaign or from a retry.\n" % cd)
        return RC_REFUSE_EXISTS
    for parent in (os.path.join(RUNS, rung),):
        stale = os.path.join(parent, level)
        if os.path.exists(stale):
            sys.stderr.write("REFUSED: %s already exists\n" % stale)
            return RC_REFUSE_EXISTS

    if verify_generator() is None:
        return RC_FAIL

    n, cells, end_time = level_spec(level)
    os.makedirs(cd)
    signal.signal(signal.SIGTERM, _sigterm)
    rc = RC_FAIL
    try:
        import cavity_ladder
        meta = cavity_ladder.build_case(cd, RE_OF[rung], n,
                                        max_iter=end_time,
                                        grading_ratio=GRADING_RATIO)
        if meta["cells"] != cells:
            raise RuntimeError("the generator built %d cells at n = %d; "
                               "section 6 registers %d"
                               % (meta["cells"], n, cells))
        meta["rung"], meta["level"] = rung, level
        meta["section_6_1"] = apply_section_6_1(cd, end_time)
        meta["generator_blob"] = CAVITY_LADDER_BLOB
        meta["predicted_core_s"] = PRED[key]
        meta["cost_basis"] = COST_BASIS[key]
        meta["wall_cap_s"] = wall_cap(key)
        meta["ranks"] = RANKS
        json.dump(meta, open(os.path.join(cd, "meta.json"), "w"), indent=2)

        if sh("blockMesh", cd, os.path.join(cd, "log.blockMesh")) != 0:
            raise RuntimeError("blockMesh failed; see log.blockMesh")
        # Mesh birth certificate (section 4.4, VERIFICATION section 9 v1.5):
        # every level runs checkMesh at creation and RETAINS log.checkMesh. A
        # level whose checkMesh is not clean does not enter the ladder --
        # grade_f11.py reads this log and grades that row NOT A RESULT.
        sh("checkMesh", cd, os.path.join(cd, "log.checkMesh"))

        # THE AGE GUARD'S ANCHOR (CLAUDE.md rule 4): 0/ is touched LAST before
        # the solver starts, so it dates the run that was allowed to produce
        # the answer. Every field and every sampled .xy must be strictly newer.
        now = time.time()
        for f in os.listdir(os.path.join(cd, "0")):
            os.utime(os.path.join(cd, "0", f), (now, now))
        time.sleep(0.01)

        rc_solve = sh("simpleFoam", cd, os.path.join(cd, "log.simpleFoam"))
        rc = RC_OK if rc_solve == 0 else RC_FAIL
        if rc != RC_OK:
            sys.stderr.write("simpleFoam rc=%d in %s\n" % (rc_solve, cd))
    except Exception as exc:                                   # noqa: BLE001
        sys.stderr.write("FAILED %s/%s: %r\n" % (rung, level, exc))
        rc = RC_FAIL
    open(os.path.join(cd, "run_rc.txt"), "w").write("%d\n" % rc)
    json.dump(dict(wall_s=time.time() - _LIVE["t0"], ranks=RANKS,
                   killed=False, predicted_core_s=PRED[key],
                   cost_basis=COST_BASIS[key]),
              open(os.path.join(cd, "launch_timing.json"), "w"), indent=2)
    return rc



# ---------------------------------------------------------------------------
# SELFTEST -- N-T8 value controls AND mutation controls (registered 792acd8f)
# ---------------------------------------------------------------------------

_CHECKS = []
_MUTATIONS = []


def check(name, ok, detail="", mutation=False):
    _CHECKS.append((name, bool(ok), detail))
    if mutation:
        _MUTATIONS.append(name)
    print("  [%s] %s%s" % ("ok " if ok else "FAIL", name,
                           "   " + detail if detail else ""))


def _refuses(fn, *a, **k):
    """Run ``fn`` and report (refused, message).  A control that only proves a
    call SUCCEEDS proves nothing about a defect; every mutation below is
    checked for an actual refusal AND for the refusal naming the right thing."""
    try:
        fn(*a, **k)
        return False, ""
    except RuntimeError as exc:
        return True, str(exc)


def selftest():
    print("rerun_f11.py --selftest")
    print("N-T8 (heat-transfer, commit 792acd8f): a control that only checks a "
          "key EXISTS is what let a\nsign defect survive 45/45.  Every control "
          "below reads a VALUE off a dictionary whose shape is\nknown by "
          "construction, and every one is paired with a MUTATION that must "
          "REFUSE.")
    tmpd = tempfile.mkdtemp(prefix="f11_rerun_selftest_")
    try:
        import cavity_ladder
        end_time = 4000
        case = os.path.join(tmpd, "case")
        os.makedirs(os.path.join(case, "system"))
        cd_path = os.path.join(case, "system", "controlDict")
        virgin = cavity_ladder.control_dict(end_time)
        open(cd_path, "w").write(virgin)

        # ------------------------------------------------------------------
        print("\n(i) the GENERATOR's dictionary is the one section 6.1 "
              "describes -- read, not assumed")
        _, _, n_prof = find_block(virgin, PROFILES_OBJECT)
        _, _, n_ser = find_block(virgin, SERIES_OBJECT)
        check("the generator emits exactly ONE '%s' object and NO '%s'"
              % (PROFILES_OBJECT, SERIES_OBJECT), n_prof == 1 and n_ser == 0,
              "found %d / %d" % (n_prof, n_ser))
        ps, pe, _ = find_block(virgin, PROFILES_OBJECT)
        vb = virgin[ps:pe]
        check("and it carries 'executeControl onEnd;' and 'writeControl "
              "onEnd;' exactly once each",
              len(re.findall(r"^\s*executeControl\s+onEnd;\s*$", vb,
                             re.M)) == 1
              and len(re.findall(r"^\s*writeControl\s+onEnd;\s*$", vb,
                                 re.M)) == 1)
        check("the untouched generator dictionary is NOT arm B -- so the "
              "asserter is not vacuous",
              _refuses(assert_arm_b_arrangement, virgin, end_time)[0],
              mutation=True)

        # ------------------------------------------------------------------
        print("\n(ii) N-T8 VALUE CONTROL: apply section 6.1 and read the "
              "arrangement back OFF DISK")
        meta = apply_section_6_1(case, end_time)
        on_disk = open(cd_path).read()
        ps, pe, n_prof = find_block(on_disk, PROFILES_OBJECT)
        ss, se, n_ser = find_block(on_disk, SERIES_OBJECT)
        pb, sb = on_disk[ps:pe], on_disk[ss:se]
        check("exactly TWO sampling objects on disk: '%s' and '%s'"
              % (PROFILES_OBJECT, SERIES_OBJECT), n_prof == 1 and n_ser == 1,
              "found %d / %d" % (n_prof, n_ser))
        check("'%s' -- the GRADED object -- is still onEnd, which is what "
              "puts its .xy under the CONVERGED iteration and satisfies the "
              "frozen C4 WITHOUT CHANGING C4" % PROFILES_OBJECT,
              len(re.findall(r"^\s*executeControl\s+onEnd;\s*$", pb,
                             re.M)) == 1
              and len(re.findall(r"^\s*writeControl\s+onEnd;\s*$", pb,
                                 re.M)) == 1
              and not re.search(r"^\s*(?:execute|write)Interval\b", pb, re.M))
        check("'%s' -- the PERIODIC object -- is timeStep / %d on both "
              "controls and carries no onEnd"
              % (SERIES_OBJECT, SERIES_INTERVAL),
              len(re.findall(r"^\s*executeControl\s+timeStep;\s*$", sb,
                             re.M)) == 1
              and len(re.findall(r"^\s*writeControl\s+timeStep;\s*$", sb,
                                 re.M)) == 1
              and len(re.findall(r"^\s*executeInterval\s+%d;\s*$"
                                 % SERIES_INTERVAL, sb, re.M)) == 1
              and len(re.findall(r"^\s*writeInterval\s+%d;\s*$"
                                 % SERIES_INTERVAL, sb, re.M)) == 1
              and "onEnd" not in sb)
        check("the two objects sample BYTE-IDENTICAL point sets, so the "
              "plateau is measured at the SAME station as the graded value",
              sets_body(pb) is not None and sets_body(pb) == sets_body(sb))
        n_pts_p = len(re.findall(r"^\s*\(\s*[-0-9.eE+]+\s+[-0-9.eE+]+\s+"
                                 r"[-0-9.eE+]+\s*\)\s*$", pb, re.M))
        n_pts_s = len(re.findall(r"^\s*\(\s*[-0-9.eE+]+\s+[-0-9.eE+]+\s+"
                                 r"[-0-9.eE+]+\s*\)\s*$", sb, re.M))
        want_pts = (len(cavity_ladder.U_ALONG_X05[1000])
                    + len(cavity_ladder.V_ALONG_Y05[1000]))
        check("each object samples the CONSTRUCTED %d points (%d + %d, the "
              "two Ghia stations lists)"
              % (want_pts, len(cavity_ladder.U_ALONG_X05[1000]),
                 len(cavity_ladder.V_ALONG_Y05[1000])),
              n_pts_p == want_pts and n_pts_s == want_pts,
              "graded %d, series %d" % (n_pts_p, n_pts_s))
        check("FIELD WRITES UNTOUCHED: the top-level 'writeInterval %d;' and "
              "'purgeWrite 1;' survive exactly once each" % end_time,
              len(re.findall(r"^\s*writeInterval\s+%d;\s*$" % end_time,
                             on_disk, re.M)) == 1
              and len(re.findall(r"^\s*purgeWrite\s+1;\s*$", on_disk,
                                 re.M)) == 1)
        check("the returned meta records arm B and not the frozen text's "
              "arrangement",
              meta["graded_writeControl"] == "onEnd"
              and meta["series_writeControl"] == "timeStep"
              and meta["series_writeInterval"] == SERIES_INTERVAL
              and meta["series_object"] == SERIES_OBJECT
              and meta["field_writes_untouched"] is True,
              meta["amendment"])
        check("everything OUTSIDE the inserted object is byte-unchanged from "
              "the generator's dictionary",
              on_disk[:ss].rstrip() + on_disk[se:] == virgin[:pe] + virgin[pe:],
              "insertion only")
        check("re-applying REFUSES rather than editing an already-edited "
              "dictionary", _refuses(apply_section_6_1, case, end_time)[0],
              mutation=True)

        # ------------------------------------------------------------------
        print("\n(iii) MUTATION CONTROLS -- each one is a way the arrangement "
              "could silently regress")

        print("      THE ONE THIS AMENDMENT EXISTS FOR: the two sampling "
              "objects COLLAPSED BACK INTO ONE")
        collapsed = on_disk[:ss] + on_disk[se:]
        ref, msg = _refuses(assert_arm_b_arrangement, collapsed, end_time)
        check("deleting '%s' -- collapsing the two objects into one -- "
              "REFUSES" % SERIES_OBJECT,
              ref and "COLLAPSED" in msg, msg[:70], mutation=True)
        # the pre-amendment arrangement: ONE object, moved onto timeStep/250.
        # This is exactly what the frozen section 6.1 asked for and what the
        # probe measured cannot satisfy C4.
        pre_amendment = re.sub(
            r"^(\s*)executeControl(\s+)onEnd;[ \t]*$",
            lambda m: ("%sexecuteControl%stimeStep;\n%sexecuteInterval%s%d;"
                       % (m.group(1), m.group(2), m.group(1), m.group(2),
                          SERIES_INTERVAL)), virgin, flags=re.M)
        pre_amendment = re.sub(
            r"^(\s*)writeControl(\s+)onEnd;[ \t]*$",
            lambda m: ("%swriteControl%stimeStep;\n%swriteInterval%s%d;"
                       % (m.group(1), m.group(2), m.group(1), m.group(2),
                          SERIES_INTERVAL)), pre_amendment, count=0, flags=re.M)
        ref, msg = _refuses(assert_arm_b_arrangement, pre_amendment, end_time)
        check("the FROZEN section 6.1 arrangement itself -- one object moved "
              "onto timeStep/%d -- REFUSES, which is the defect the "
              "2026-08-25 amendment repairs" % SERIES_INTERVAL,
              ref and "COLLAPSED" in msg, msg[:70], mutation=True)

        print("      and the other regressions")
        moved = on_disk[:ps] + re.sub(
            r"^(\s*)(executeControl|writeControl)(\s+)onEnd;[ \t]*$",
            lambda m: "%s%s%stimeStep;" % (m.group(1), m.group(2), m.group(3)),
            pb, flags=re.M) + on_disk[pe:]
        ref, msg = _refuses(assert_arm_b_arrangement, moved, end_time)
        check("moving the GRADED object off onEnd REFUSES", ref,
              msg[:70], mutation=True)
        left = on_disk[:ss] + sb.replace("timeStep;", "onEnd;") + on_disk[se:]
        check("leaving the PERIODIC object on onEnd REFUSES",
              _refuses(assert_arm_b_arrangement, left, end_time)[0],
              mutation=True)
        skew = on_disk[:ss] + sb.replace("0.9766", "0.9765", 1) + on_disk[se:]
        ref, msg = _refuses(assert_arm_b_arrangement, skew, end_time)
        check("a series that samples DIFFERENT points from the graded object "
              "REFUSES", ref and "same points" in msg, msg[:70], mutation=True)
        touched = on_disk.replace("writeInterval   %d;" % end_time,
                                  "writeInterval   %d;" % (end_time // 2), 1)
        check("touching the top-level field 'writeInterval' REFUSES",
              _refuses(assert_arm_b_arrangement, touched, end_time)[0],
              mutation=True)
        no_purge = re.sub(r"^\s*purgeWrite\s+1;\s*$", "", on_disk,
                          count=1, flags=re.M)
        check("dropping 'purgeWrite 1;' REFUSES",
              _refuses(assert_arm_b_arrangement, no_purge, end_time)[0],
              mutation=True)
        dup = on_disk[:se] + "\n" + sb + on_disk[se:]
        ref, msg = _refuses(assert_arm_b_arrangement, dup, end_time)
        check("a DUPLICATE '%s' object REFUSES -- two periodic objects are "
              "not arm B either" % SERIES_OBJECT,
              ref and "found 2" in msg, msg[:70], mutation=True)
        # and the WHOLE-DICTIONARY counting argument, which the two block
        # reads above cannot make: a stray control OUTSIDE both objects leaves
        # each block byte-perfect and must still refuse.
        stray = re.sub(r"^([ \t]*purgeWrite[ \t]+1;[ \t]*)$",
                       lambda m: m.group(1) + "\n    writeControl    onEnd;",
                       on_disk, count=1, flags=re.M)
        ps_s, pe_s, _ = find_block(stray, PROFILES_OBJECT)
        ss_s, se_s, _ = find_block(stray, SERIES_OBJECT)
        check("the stray-control mutant leaves BOTH sampling blocks "
              "byte-identical, so only the whole-dictionary counts can catch "
              "it (control on the control below)",
              stray[ps_s:pe_s] == pb and stray[ss_s:se_s] == sb)
        ref, msg = _refuses(assert_arm_b_arrangement, stray, end_time)
        check("an 'onEnd' control living OUTSIDE the graded object REFUSES on "
              "the whole-dictionary counting argument, not on the block reads",
              ref and ("does not have arm B's shape" in msg
                       or "lives outside" in msg), msg[:70], mutation=True)
        check("an endTime equal to the sampling interval REFUSES rather than "
              "assert something that cannot discriminate the two writes",
              _refuses(assert_arm_b_arrangement, on_disk, SERIES_INTERVAL)[0],
              mutation=True)
        check("CONTROL ON THE CONTROLS: the UNMUTATED dictionary still "
              "passes, so the %d refusals above are not vacuous"
              % len(_MUTATIONS),
              not _refuses(assert_arm_b_arrangement, on_disk, end_time)[0])

        # ------------------------------------------------------------------
        print("\n(iv) the budget arithmetic of section 7, unchanged by this "
              "amendment")
        frozen_caps = {("re1000", "coarse"): 60, ("re1000", "medium"): 60,
                       ("re1000", "fine"): 442, ("re100", "coarse"): 60,
                       ("re100", "medium"): 60, ("re100", "fine"): 674}
        bad = {k: (round(wall_cap(k)), v) for k, v in frozen_caps.items()
               if round(wall_cap(k)) != v}
        check("max(60, 2.5 x predicted) reproduces section 7's frozen per-run "
              "caps 60/60/442/60/60/674", not bad, str(bad))
        cap_sum = sum(wall_cap(k) for k in frozen_caps)
        check("the per-run caps sum ABOVE the %.0f core-s budget, so the "
              "WATCHDOG is the binding enforcement" % CAP_CORE_S,
              cap_sum > CAP_CORE_S, "%.3f s" % cap_sum)
        check("DOCUMENT DEFECT, recorded not repaired: section 7 states the "
              "caps sum to 1,296 s where its own six caps sum to 1,355.575 s "
              "-- IMMATERIAL, both are far above 780 s and the conclusion "
              "holds a fortiori", abs(cap_sum - 1355.575) < 1e-3,
              "discrepancy %.3f s" % (cap_sum - 1296.0))
        check("the four waves still sum to the frozen 8.02 core-min "
              "prediction", abs(sum(PRED.values()) / 60.0 - 8.02) < 0.005,
              "%.4f core-min" % (sum(PRED.values()) / 60.0))
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)

    n_ok = sum(1 for _, ok, _ in _CHECKS if ok)
    print("\n%d/%d checks passed" % (n_ok, len(_CHECKS)))
    print("%d of them are MUTATION controls -- each proves the launcher "
          "REFUSES when the dictionary it\nwrote is not arm B's arrangement, "
          "including the collapse back into a single sampling object."
          % len(_MUTATIONS))
    if n_ok != len(_CHECKS):
        print("\nFAILED: " + "; ".join(n for n, ok, _ in _CHECKS if not ok))
    return RC_OK if n_ok == len(_CHECKS) else RC_FAIL


# ---------------------------------------------------------------------------
# parent: waves, pre-wave budget check, global watchdog
# ---------------------------------------------------------------------------

def load_reading():
    """Section 7: load is checked before each wave.  RECORDED, not gated -- no
    load threshold is registered in the pre-registration and inventing one here
    would be inventing a clause.  Other teams' solvers are observed and never
    touched."""
    try:
        la1, la5, la15 = os.getloadavg()
    except OSError:
        la1 = la5 = la15 = None
    return dict(loadavg_1min=la1, loadavg_5min=la5, loadavg_15min=la15,
                cpu_count=os.cpu_count(),
                note="recorded, NOT gated; this launcher signals only "
                     "processes it started itself")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--dry-run", action="store_true",
                    help="print the frozen matrix, caps and budget arithmetic "
                         "and launch NOTHING")
    ap.add_argument("--selftest", action="store_true",
                    help="run the value and mutation controls on the section "
                         "6.1 dictionary surgery and launch NOTHING")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    total_pred = sum(PRED.values())
    if a.dry_run:
        print("F11 CONVERSION -- launcher, DRY RUN. Nothing is launched.")
        print("  cap %.1f core-min = %.0f core-s (HARD; an overrun stops the "
              "run)" % (CAP_CORE_MIN, CAP_CORE_S))
        print("  predicted total %.2f core-s = %.4f core-min"
              % (total_pred, total_pred / 60.0))
        print("  per-run wall caps sum to %.1f s, ABOVE the budget -- the "
              "watchdog is the binding enforcement"
              % sum(wall_cap(k) for k in PRED))
        cum = 0.0
        for i, wave in enumerate(WAVES, 1):
            cum += sum(PRED[k] for k in wave)
            print("  wave %d: %-34s pred %7.2f core-s  cum %.2f core-min"
                  % (i, ", ".join("/".join(k) for k in wave),
                     sum(PRED[k] for k in wave), cum / 60.0))
        for k in PRED:
            print("    %-16s n=%-4d endTime %-5d wall cap %6.1f s  pred "
                  "%7.2f core-s  [%s]"
                  % ("/".join(k), level_spec(k[1])[0], level_spec(k[1])[2],
                     wall_cap(k), PRED[k], COST_BASIS[k]))
        print("  generator %s blob %s: %s"
              % (CAVITY_LADDER_REL, CAVITY_LADDER_BLOB,
                 "VERIFIED byte-unchanged" if verify_generator()
                 else "MISMATCH -- would refuse"))
        return RC_OK

    if verify_generator() is None:
        return RC_FAIL
    os.makedirs(RUNS, exist_ok=True)
    ledger = dict(cap_core_min=CAP_CORE_MIN, cap_core_s=CAP_CORE_S,
                  predicted_total_core_s=total_pred, ranks=RANKS,
                  runs={}, waves={}, stopped_by=None,
                  cost_basis_note="core-minutes = wall s x ranks / 60 and are "
                                  "the MEASURED unit. Dollars are DERIVED at "
                                  "the owner-stated $0.0513/core-h; this box "
                                  "cannot read its own billing "
                                  "(COMPUTE_BUDGET_CHARTER section 5). A "
                                  "docs/COST_CALIBRATION.md row is MANDATORY "
                                  "at completion.")
    ledger_path = os.path.join(HERE, "F11_CONVERSION_RUN_LEDGER.json")

    def flush():
        ledger["spent_core_min"] = round(spent_s / 60.0, 4)
        ledger["cap_respected"] = spent_s <= CAP_CORE_S
        json.dump(ledger, open(ledger_path, "w"), indent=2)

    spent_s = 0.0
    stopped = False
    for wi, wave in enumerate(WAVES, 1):
        ledger["waves"][str(wi)] = dict(runs=["/".join(k) for k in wave],
                                        load_before=load_reading(),
                                        predicted_core_s=sum(PRED[k]
                                                             for k in wave))
        if stopped:
            for k in wave:
                ledger["runs"]["/".join(k)] = dict(
                    status="PENDING",
                    reason="the budget stopped the line before wave %d; a "
                           "triple is never left half-built, so a whole rung "
                           "is lost, never one level" % wi)
            continue

        # ---- enforcement point 2: the pre-wave budget check ---------------
        pred_wave = sum(PRED[k] for k in wave)
        if spent_s + pred_wave * WAVE_HEADROOM > CAP_CORE_S:
            for k in wave:
                ledger["runs"]["/".join(k)] = dict(
                    status="PENDING",
                    reason="wave %d not launched: %.2f spent + %.2f predicted "
                           "x %.2f headroom exceeds the %.0f core-s cap"
                           % (wi, spent_s, pred_wave, WAVE_HEADROOM,
                              CAP_CORE_S))
            ledger["stopped_by"] = ("pre-wave budget check before wave %d"
                                    % wi)
            stopped = True
            flush()
            continue

        procs = {}
        for k in wave[:MAX_CONCURRENT]:
            cmd = [sys.executable, os.path.abspath(__file__), "--one",
                   k[0], k[1]]
            procs[k] = dict(p=subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                               stderr=subprocess.PIPE),
                            t0=time.time())
            print("[wave %d] launched %s (cap %.0f s, pred %.2f core-s)"
                  % (wi, "/".join(k), wall_cap(k), PRED[k]), flush=True)

        # ---- enforcement points 1 and 3: wall caps and the global watchdog -
        while any(v["p"].poll() is None for v in procs.values()):
            time.sleep(WATCHDOG_POLL_S)
            for v in procs.values():
                if v["p"].poll() is not None and "wall" not in v:
                    v["wall"] = time.time() - v["t0"]
            live_s = sum(time.time() - v["t0"] for v in procs.values()
                         if v["p"].poll() is None)
            done_s = sum(v["wall"] for v in procs.values() if "wall" in v)
            if (spent_s + live_s + done_s) * RANKS >= CAP_CORE_S:
                for k, v in procs.items():
                    if v["p"].poll() is None:
                        v["p"].send_signal(signal.SIGTERM)
                        v["killed"] = ("global watchdog: cumulative core-s "
                                       "reached the %.0f s cap" % CAP_CORE_S)
                ledger["stopped_by"] = ("global watchdog reached the %.1f "
                                        "core-min cap" % CAP_CORE_MIN)
                stopped = True
                break
            for k, v in procs.items():
                if v["p"].poll() is None and \
                        (time.time() - v["t0"]) > wall_cap(k):
                    v["p"].send_signal(signal.SIGTERM)
                    v["killed"] = "per-run wall cap %.0f s" % wall_cap(k)

        for k, v in procs.items():
            v["p"].wait()
            v.setdefault("wall", time.time() - v["t0"])
            spent_s += v["wall"] * RANKS
            name = "/".join(k)
            status = ("KILLED" if "killed" in v else
                      ("OK" if v["p"].returncode == 0 else
                       ("REFUSED_EXISTS"
                        if v["p"].returncode == RC_REFUSE_EXISTS
                        else "FAILED")))
            ledger["runs"][name] = dict(
                status=status, killed_reason=v.get("killed"),
                rc=v["p"].returncode, predicted_core_s=PRED[k],
                actual_core_s=round(v["wall"] * RANKS, 2),
                ratio_actual_over_predicted=round(v["wall"] * RANKS
                                                  / PRED[k], 3),
                cost_basis=COST_BASIS[k], ranks=RANKS,
                wall_cap_s=wall_cap(k), case_dir=case_dir(k),
                stderr_tail=(v["p"].stderr.read().decode()[-1200:]
                             if v["p"].stderr else ""))
            print("[wave %d] %-16s %-14s %7.1f core-s (pred %6.2f)  "
                  "cum %.3f core-min"
                  % (wi, name, status, v["wall"] * RANKS, PRED[k],
                     spent_s / 60.0), flush=True)
        flush()
        if stopped:
            for later in WAVES[wi:]:
                for k in later:
                    ledger["runs"].setdefault("/".join(k), dict(
                        status="PENDING",
                        reason="the budget stopped the line at wave %d" % wi))
            break

    flush()
    print("\nTOTAL %.4f core-min against a %.1f core-min cap (respected: %s)"
          % (spent_s / 60.0, CAP_CORE_MIN, ledger["cap_respected"]))
    print("predicted %.4f core-min; ratio actual/predicted = %.3f"
          % (total_pred / 60.0,
             (spent_s / total_pred) if total_pred else float("nan")))
    print("ledger: %s" % ledger_path)
    print("A docs/COST_CALIBRATION.md row is MANDATORY at completion "
          "(CLAUDE.md rule 12, section 7): actual core-minutes from the logs, "
          "the ratio actual/predicted, and the gap attributed between "
          "contention, waste and misprediction -- waste named separately and "
          "never absorbed into the ratio.")
    return RC_OK if ledger["cap_respected"] else RC_FAIL


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--one":
        sys.exit(run_one_child(sys.argv[2], sys.argv[3]))
    sys.exit(main())
