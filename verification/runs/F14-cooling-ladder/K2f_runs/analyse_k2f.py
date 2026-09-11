#!/usr/bin/env python3
"""analyse_k2f.py -- K2f comparator.  F14 cooling ladder, rack-row module.

    python3 analyse_k2f.py <case_root>     GRADE the ladder under <case_root>
    python3 analyse_k2f.py --selftest      mutation matrix + the wiring audit
    python3 analyse_k2f.py --xcheck        reproduce a PUBLISHED triple exactly

REGISTRATION
------------
`docs/campaigns/F14-cooling-ladder/K2f_PREREGISTRATION.md`.  Every gate,
threshold, band, floor and label below is that document's; this file implements
them and invents none.

WHY THIS FILE EXISTS, IN ONE PARAGRAPH
--------------------------------------
`analyse_k2d.py` was frozen with **31 green selftest arms** and a `main()` that
graded nothing: `analyse_k2d.py:613-619` is a two-branch stub -- `--selftest`,
or a hardcoded refusal -- and `read_checkmesh`, `read_patch_census`,
`gate_mincell` and `built_cell_count` each took a `case_dir` that `main()` never
supplied.  The rung was ungradeable at ALL THREE LEVELS, not merely the one that
timed out.  The heat-transfer supervisor's standing correction, recorded under
their own name:

    A SELFTEST COUNT IS EVIDENCE ABOUT GATE FUNCTIONS AND EVIDENCE ABOUT
    NOTHING ELSE.  THE CHECK IS THAT A COMPARATOR CAN BE POINTED AT A CASE
    DIRECTORY AND RETURN A VERDICT.

and the deeper one:

    A FREEZE VERIFIES BYTES AND NEVER VERIFIES THAT ANYTHING CALLS THEM.

`--selftest` therefore carries `wiring_audit()`, which parses THIS FILE'S OWN
AST, walks the call graph from `main`, and FAILS if any registered gate function
is unreachable from it.  That is the executable form of the correction: a gate
function nobody calls is a defect the selftest can now SEE, and K2d's four
orphans would have failed it.

EXIT MAP -- T3's convention, registration s.9.5
    0 EXIT_OK      the comparator ran and emitted a verdict set
    1 EXIT_FAIL    a selftest arm did not behave as registered
    2 EXIT_REFUSE  a named limb refused; NOTHING was graded

**THE EXIT CODE DOES NOT CARRY THE VERDICT.**  T16c returned `rc = 0` while
every row read `NOT A RESULT`.  The verdict is read from the gate JSON and from
stdout, never from `$?`.

WHAT IS CALLED RATHER THAN REIMPLEMENTED
----------------------------------------
  * `scripts/roache_triple.py`      -- ratios, GCI, triple classification,
    `monotone`, `NOT_A_RESULT_STATES`, `band_verdict`, `PLANT`,
    `external_plant_control`, `assert_plant_control`.  Cross-checked against a
    PUBLISHED triple by `--xcheck` before it is trusted (see below).
  * `scripts/check_convergence.py`  -- `classify_monitor` (S13) for the G-CYCLE
    spread, which carries D389's range-spanned normaliser and the
    null-variation refusal, and `monitor_series` for the read itself.
    Thresholds come from `docs/physics_rules.yaml` AT RUN TIME (s.6.1) and are
    ASSERTED against the registered numbers -- a yaml that has drifted from the
    registration is a REFUSAL, never a silent regrade.
  * `mark_done_k2f.py`              -- all six clauses of standing rule 4, and
    clause 7.  There is ONE implementation of the completion rule for this rung.

WHERE RULE 5's ORDER IS LOCAL, AND WHY -- STATED RATHER THAN GLOSSED
--------------------------------------------------------------------
`roache_triple.grade_ladder` is the lab's rule-5 entry point and it bands on the
FINE VALUE (`band_verdict(fine_value, band)`, `roache_triple.py:594`).  **K2f's
registered band is on the OBSERVED ORDER** -- `p in (0.5, 3.5)`, registration
s.5.3 -- so `grade_ladder` cannot be this rung's entry point as written, and
saying otherwise would be laundering.  What is done instead:

  * every ARITHMETIC primitive is the shared one (`all_triples`, `monotone`,
    `NOT_A_RESULT_STATES`), and so is the BAND COMPARISON itself
    (`RT.band_verdict(order, ORDER_BAND)`);
  * only the ORDER of rule 5's three steps is written here, and `--selftest`
    carries an arm that drives a VALUE-banded ladder through BOTH this file's
    ordering and `RT.grade_ladder` and REQUIRES THE SAME VERDICT.  The shared
    instrument stays the authority on the ordering; this file is checked
    against it rather than trusted beside it.

This is reported to the supervisor as a finding about the registration, not
worked around in silence.

THE CROSS-CHECK, BEFORE THE INSTRUMENT IS TRUSTED
-------------------------------------------------
`--xcheck` reproduces T23G2R's published Q4 triple exactly -- cells
(40320, 90720, 204120), values (53.58204022, 52.94243232, 52.51458586),
dim = 2 -- against `verification/runs/T-family/T23G2R_runs/
T23G2R_COMPARATOR_STDOUT.txt:125`, which reads **order 0.9917, GCI 2.0576 %**.
It runs INSIDE `--selftest` too, so the citation sits in an executable check
(CLAUDE.md rule 6) rather than in a comment that can rot.

THE TWO PRE-FREEZE OBLIGATIONS THIS FILE IS BUILT TO SATISFY
------------------------------------------------------------
  * `A-DRIVE` (s.7)   -- `main()` takes a case root and returns a verdict, in
    both directions, recorded in `K2f_DRIVE_ARM_DEMONSTRATION.txt`.
  * `A-INPUT` (s.3.1) -- the gate's INPUTS are asserted to exist on disk and be
    non-empty, and a case whose `functions` block was removed must REFUSE at
    exit 2 rather than return a zero or a green, recorded in
    `K2f_INPUT_ARM_DEMONSTRATION.txt`.  **This is standing rule 3's principle
    applied to the gate's INPUT rather than to its reader**: a gate whose input
    was never written fails SILENTLY, and nothing in K2d would have caught it.

WHAT THIS COMPARATOR REFUSES TO DO
----------------------------------
  * It never grades a row whose series file is absent, empty, or matched by more
    than one path (OpenFOAM writes a SECOND function-object file on restart
    rather than overwriting the first, and both match the glob -- a WRONG NUMBER
    rather than a crash).
  * It never quotes a GCI when the three values are not monotone.
  * It never returns a zero from a reader not shown able to see a non-zero.
  * It never reports `CONVERGED` without the measured detection floor beside it.
  * It never rehabilitates a row upward.  The gate is ONE-WAY and `_seal_oneway`
    raises rather than asserts, so `-O` cannot strip the check.
"""

import ast
import glob
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo(start):
    """Walk up to the repo root by LOOKING FOR IT, not by counting dirnames.

    A hard-coded chain of `os.path.dirname()` calls is a silent breakage the day
    the tree is reorganised -- the `cost_channel.py` defect class, and it bit
    `analyse_k2d.py` on its first run with three levels where four were needed.
    Search for the marker, and REFUSE rather than importing a shared instrument
    from whatever happens to be on `sys.path`.
    """
    d = start
    while True:
        if (os.path.isdir(os.path.join(d, "scripts"))
                and os.path.isfile(os.path.join(d, "CLAUDE.md"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise SystemExit(
                "REFUSE (exit 2): cannot locate the repository root above %s -- "
                "refusing to import a shared instrument from an unverified path"
                % start)
        d = parent


REPO = _find_repo(HERE)
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT                                    # noqa: E402
import check_convergence as CC                                # noqa: E402
import mark_done_k2f as MD                                    # noqa: E402
import build_k2f as BK                                        # noqa: E402

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# ---------------------------------------------------------------------------
# REGISTERED CONSTANTS.  Every one of these cites the section that fixes it.
# ---------------------------------------------------------------------------
LEVELS = ("K2f_L1", "K2f_L2", "K2f_L3")       # s.9.2 allow-list, == MD.CASES
DIM = 3                                       # s.1: 3D, r = 1.5 in 3 directions

MESHSIM_LO, MESHSIM_HI = 3.2063, 3.5438       # s.1   3.375 +- 5 %
ORDER_LO, ORDER_HI = 0.5, 3.5                 # s.5.3 the widened band
SUBFIRST = 1.0                                # s.5.3 A-SUBFIRST annotation
MINCELL_FLOOR_M = 5.0e-3                      # s.5.4 G-MINCELL floor
FS = 1.25                                     # s.5.2 GCI safety factor

CYCLE_TOL_PCT = 0.02                          # s.6.1 of RANGE SPANNED
CYCLE_WINDOW = 400                            # s.6.1 last 400 iterations
CYCLE_INTERVAL = 50                           # s.6.1 sample cadence
CYCLE_MIN_SAMPLES = 9                         # s.6.1 REFUSED below this
SIGN_CHANGES_MIN = 3                          # s.6.1 CYCLING limb
TREND_FRAC_MAX = 0.25                         # s.6.1 CYCLING limb
FLOOR_FRACTIONS = (1.0, 0.5, 0.25, 0.125, 0.0625)   # s.6.2 measured floor

# G-CHECKMESH tolerance registry.  EMPTY = ZERO TOLERANCE (s.5.4).  An entry may
# only be added BEFORE the freeze and must carry its own written justification.
MESHQ_TOLERANCE = {}

NAMED_FEATURES = BK.NAMED_FEATURES             # one definition, the builder's
T_SUP = BK.T_SUP                               # s.2, K2a defaults
DT_RACK = BK.DT_RACK
N_RACKS = BK.N_RACKS

# Registered graded rows, s.5.1.  `series` names the producer(s) the row is
# built from; `derived` says the row has no single producer and why.
GRADED_ROWS = {
    "G1": dict(quantity="T_in,max", unit="K", derived=True,
               why="max over i of the per-rack T_in_i patch averages"),
    "G2": dict(quantity="theta_max", unit="-", derived=True,
               why="(T_in,max - T_SUP) / DT_RACK, an affine map of G1"),
    "G3": dict(quantity="T_in,end", unit="K", derived=False,
               why="the end rack, where end effects are largest"),
    "G4": dict(quantity="T_ca", unit="K", derived=False,
               why="volume-averaged T over the cold-aisle cellZone"),
}

# THE END-RACK INDEX, REGISTERED HERE BECAUSE TWO CONVENTIONS COLLIDE.
# Registration s.5.1 names row G3 `T_in,1` in a ONE-BASED rack numbering; the
# builder writes `rack0_in .. rack3_in`, ZERO-BASED.  The registration's own
# parenthetical settles which physical rack is meant -- "the end rack, where end
# effects are largest" -- and that is the builder's rack 0, at x in [0.6, 1.2],
# against the row's outer end.  The comparator uses index 0 and PRINTS THE
# MAPPING on every run, because an off-by-one that nobody prints is the kind of
# defect a frozen document preserves rather than catches.
END_RACK_INDEX = 0

# The two quantities G-CYCLE is evaluated on, s.5.2 step 2.
CYCLE_QUANTITIES = ("T_in,max", "U_ha")

# The .dat reader's row pattern: EXACTLY TWO COLUMNS, `time value`.  Handed to
# `CC.classify_monitor` and to `CC.monitor_series`, so the shared instrument
# reads the registered artifact directly rather than a copy this file made.
DAT_VALUE_RE = r"(?m)^\s*[0-9]\S*\s+([-+0-9.eE]+)\s*$"


class Refuse(Exception):
    pass


def refuse(msg):
    raise Refuse(msg)


# ---------------------------------------------------------------------------
# artifact resolution
# ---------------------------------------------------------------------------
def resolve_unique(pattern):
    """Refuse when a glob matches more than one file where one is expected.

    Clause 7 should make this unreachable.  It is here anyway because A GUARD
    AND A READER THAT BOTH CHECK is the pattern that saved K2bU3R3, whose launch
    guard was live and enforcing while the rest of its instrument could not
    execute at all.  One of the two being dead must not be enough to produce a
    number.
    """
    hits = sorted(glob.glob(pattern))
    if not hits:
        refuse("no file matches %s -- the gate's INPUT was never produced. "
               "A-INPUT (s.3.1): a gate whose input was never written fails "
               "SILENTLY, and this comparator refuses rather than returning a "
               "zero or a green." % pattern)
    if len(hits) > 1:
        refuse("GLOB COLLISION: %d files match %s -- %s. OpenFOAM writes a "
               "SECOND function-object file on restart rather than overwriting "
               "the first, so reading either is a WRONG NUMBER, not a crash. "
               "This reader refuses rather than picking one."
               % (len(hits), pattern, ", ".join(os.path.basename(h) for h in hits)))
    return hits[0]


def series_path(case_dir, name):
    """The one file a named function-object series was written to, or REFUSE."""
    fo_file = "volFieldValue.dat" if name in ("U_ha", "T_ca") else "surfaceFieldValue.dat"
    return resolve_unique(os.path.join(case_dir, "postProcessing", name, "*", fo_file))


def read_dat_series(path):
    """THE PRODUCTION READ PATH.  Returns (iterations, values, raw strings).

    This is the function the planted-zero control plants into and reads back
    through, so a zero it returns is a statement about the FILE rather than
    about the reader (standing rule 3).

    Refuses a row that is not exactly two columns, because `DAT_VALUE_RE` --
    which `CC.classify_monitor` is handed -- assumes two, and a reader whose
    regex silently stops matching returns FEWER SAMPLES rather than an error.
    """
    if not os.path.isfile(path):
        refuse("%s does not exist" % path)
    its, vals, raw, ncols = [], [], [], set()
    with open(path, errors="replace") as fh:
        for ln in fh:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            ncols.add(len(parts))
            try:
                its.append(float(parts[0]))
                vals.append(float(parts[-1]))
            except (ValueError, IndexError):
                refuse("%s carries an unparseable data row %r" % (path, s[:80]))
            raw.append(parts[-1])
    if not vals:
        refuse("%s exists but carries NO data row -- the gate's input is EMPTY. "
               "A-INPUT (s.3.1) refuses an empty series exactly as it refuses an "
               "absent one." % path)
    if ncols != {2}:
        refuse("%s has data rows with %s columns; this reader and the regex "
               "handed to check_convergence.classify_monitor both require "
               "exactly 2 (`time value`). REFUSED rather than read partially."
               % (path, sorted(ncols)))
    return its, vals, raw


def materialise_dat(iters, values, path):
    """Write a DERIVED series in the producer's own two-column format.

    `T_in,max` and `theta_max` have no OpenFOAM producer -- see
    `build_k2f._functions_block` -- so they are computed here from the
    per-rack series and written out in the SAME format, so that the SAME shared
    classifier reads them by the SAME path.  The primitives they are computed
    from each carry their own planted-zero control; this file does not.
    """
    with open(path, "w") as fh:
        fh.write("# Derived by analyse_k2f.py -- no OpenFOAM producer exists\n")
        fh.write("# Time            value\n")
        for t, v in zip(iters, values):
            fh.write("%-16.10g %.10g\n" % (t, v))
    return path


# ---------------------------------------------------------------------------
# A-INPUT -- the gate's INPUTS exist, s.3.1
# ---------------------------------------------------------------------------
def gate_input(case_dir):
    """A-INPUT.  Every registered series exists on disk and is non-empty.

    THIS IS THE LIMB K2d DID NOT HAVE.  K2d registered `T_in,max` and `U_ha` as
    in-pass function-object output and its pinned builder emitted NO function
    objects: `grep -c functions` returned 0 on all three controlDicts and no
    `postProcessing/` was ever created.  `G-CYCLE` had no input at ANY level and
    31 green comparator arms saw nothing, because every one of them tested a
    gate FUNCTION against a synthetic series it had made itself.

    Returns (ok, message, detail).  A missing or empty series REFUSES.
    """
    found, detail = [], {}
    for name in BK.SERIES:
        path = series_path(case_dir, name)          # refuses on absent/collision
        its, vals, raw = read_dat_series(path)      # refuses on empty/ragged
        res = CC.print_resolution(raw, vals[-1])
        detail[name] = dict(path=path, n_samples=len(vals), last=vals[-1],
                            first_iteration=its[0], last_iteration=its[-1],
                            print_resolution=res,
                            run_range=max(vals) - min(vals))
        found.append(name)
    cadences = {n: (d["last_iteration"] - d["first_iteration"]) / max(1, d["n_samples"] - 1)
                for n, d in detail.items() if d["n_samples"] > 1}

    # THE CADENCE ASSERTION, AND IT IS THE SAME DEFECT CLASS AS THE TWO THIS
    # RUNG EXISTS FOR.  `check_convergence.classify_monitor` takes the number of
    # samples in the window as `window_iterations // sample_interval_iterations
    # + 1` -- 400 // 50 + 1 = 9 -- READ FROM THE THRESHOLD FILE.  It never looks
    # at the time column of the series it was handed, so a series written at any
    # other cadence is silently windowed over the WRONG NUMBER OF ITERATIONS and
    # returns a state rather than an error.  A 2-iteration cadence would have its
    # last 9 samples treated as spanning 400.  Nothing in the lab asserts that
    # the producer's cadence is the classifier's, so this rung asserts it: the
    # registered cadence is s.6.1's 50, the builder writes `executeInterval 50`,
    # and a series that disagrees REFUSES rather than being graded on a window
    # that is not the registered one.
    off = {n: c for n, c in cadences.items() if abs(c - CYCLE_INTERVAL) > 1e-9}
    if off:
        refuse("A-INPUT CADENCE: %s written at %s iterations per sample, but "
               "registration s.6.1 registers a %d-iteration cadence and "
               "check_convergence.classify_monitor sizes its window from that "
               "number WITHOUT READING THE SERIES' OWN TIME COLUMN. A series at "
               "another cadence would be windowed over the wrong span and would "
               "return a STATE rather than an error. REFUSED."
               % (", ".join(sorted(off)),
                  ", ".join("%s=%g" % (k, v) for k, v in sorted(off.items())),
                  CYCLE_INTERVAL))
    return True, ("A-INPUT PASS: all %d registered series present and non-empty "
                  "(%s); sample cadences %s"
                  % (len(found), ", ".join(found),
                     ", ".join("%s=%g" % (k, v) for k, v in cadences.items()))), detail


# ---------------------------------------------------------------------------
# standing rule 3 -- the planted-zero control ON THE READER
# ---------------------------------------------------------------------------
def planted_zero_control(case_dir, name):
    """Plant `RT.PLANT` into a COPY of the real series on disk, BY LINE INDEX,
    read it back THROUGH `read_dat_series` -- the production reader -- and
    REFUSE if the reader cannot see it.

    T3's pattern (`analyse_t3.py:287` `plant_into_T`, refusal at `:801`) and
    `analyse_t10a.py:846`, on THIS rung's artifact.  A negative arm re-reads the
    UNPLANTED copy and requires the original value back, so the control cannot
    pass by the reader returning the planted number unconditionally.

    The result is wrapped by `RT.external_plant_control` and checked by
    `RT.assert_plant_control`, so the refusal text is the shared one.
    """
    path = series_path(case_dir, name)
    _its, vals, _raw = read_dat_series(path)
    before = vals[-1]

    tmp = tempfile.mkdtemp(prefix="k2f_plant_")
    try:
        work = os.path.join(tmp, os.path.basename(path))
        shutil.copy(path, work)

        # NEGATIVE ARM FIRST: the untouched copy must read back the original.
        _i, v_clean, _r = read_dat_series(work)
        if v_clean[-1] != before:
            refuse("PLANTED-ZERO NEGATIVE ARM FAILED on %s: an untouched copy "
                   "read back %r where the original reads %r. The reader is not "
                   "reading the file." % (name, v_clean[-1], before))

        # POSITIVE ARM: plant BY LINE INDEX into the last data row.
        lines = open(work, errors="replace").read().split("\n")
        idx = max(i for i, ln in enumerate(lines)
                  if ln.strip() and not ln.strip().startswith("#"))
        parts = lines[idx].split()
        parts[-1] = repr(before + RT.PLANT)
        lines[idx] = " ".join(parts)
        open(work, "w").write("\n".join(lines))

        _i, v_plant, _r = read_dat_series(work)
        after = v_plant[-1]

        pc = RT.external_plant_control("read_dat_series", before, after,
                                       plant=RT.PLANT, artifact=path, level=name)
        RT.assert_plant_control(pc)     # shared refusal text, shared tolerance

        # AND the SAME plant must be visible along the GATE'S OWN PATH, which
        # is check_convergence, not this reader.  A control that proves only the
        # local reader can see a plant says nothing about the classifier that
        # actually produces the state.
        seen = CC.monitor_series([work], DAT_VALUE_RE)
        if not seen or abs((seen[-1] - before) - RT.PLANT) > RT.PLANT_READBACK_TOL:
            refuse("PLANTED-ZERO CONTROL FAILED on %s ALONG THE GATE'S OWN PATH: "
                   "check_convergence.monitor_series saw %r where %r was planted. "
                   "The local reader seeing the plant is not evidence about the "
                   "classifier that produces the state." % (name, seen[-1:], RT.PLANT))
        pc["gate_path_reader"] = "check_convergence.monitor_series"
        pc["gate_path_delta"] = seen[-1] - before
        return pc
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# G-CYCLE -- s.6.1, THROUGH the shared classifier
# ---------------------------------------------------------------------------
def assert_registered_thresholds(th):
    """The yaml is the source at run time (s.6.1); the REGISTRATION is the
    authority.  A yaml that has drifted from the registered numbers is a
    REFUSAL, never a silent regrade -- a threshold file nobody compares is the
    same defect as a frozen file nobody calls.
    """
    want = {"peak_to_peak_max_pct": CYCLE_TOL_PCT,
            "window_iterations": CYCLE_WINDOW,
            "sample_interval_iterations": CYCLE_INTERVAL,
            "min_samples": CYCLE_MIN_SAMPLES}
    bad = {k: (th.get(k), v) for k, v in want.items() if th.get(k) != v}
    if bad:
        refuse("G-CYCLE THRESHOLD DRIFT: %s supplied %s where registration s.6.1 "
               "registers %s. The comparator refuses rather than grading on a "
               "threshold the registration did not fix."
               % (th.get("source"),
                  {k: g for k, (g, _w) in bad.items()},
                  {k: w for k, (_g, w) in bad.items()}))
    return th


def classify_cycle(dat_path, label):
    """CONVERGED / CYCLING / DRIFTING, s.6.1.

    The SPREAD limb is `check_convergence.classify_monitor` -- S13 -- called on
    the artifact itself.  That is what carries D389's range-spanned normaliser
    (`heat_monitor_normaliser: range_spanned_over_run`) and the null-variation
    refusal, and reimplementing either here is how a case script drifts from the
    lab's own criterion.  `analyse_k2d.py:318` DID reimplement it; registration
    s.6.1 says both limbs CALL the shared one, and this file does.

    The CYCLING/DRIFTING split is K2f's own discrimination on the same window,
    read through the same shared reader.
    """
    cm = CC.classify_monitor([dat_path], DAT_VALUE_RE)
    th = assert_registered_thresholds(cm["thresholds"])

    if cm["status"] == "CANNOT_TELL":
        refuse("G-CYCLE CANNOT BE EVALUATED for %s: %s -- this is the "
               "NULL-VARIATION REFUSAL and it is a refusal, NOT a state. A "
               "quantity that cannot move scores perfectly on a test of whether "
               "it has stopped moving." % (label, cm.get("reason")))

    series = CC.monitor_series([dat_path], DAT_VALUE_RE)
    n_window = th["window_iterations"] // th["sample_interval_iterations"] + 1
    if len(series) < max(th["min_samples"], n_window):
        refuse("G-CYCLE: %s has %d samples, fewer than the registered %d needed "
               "to span a %d-iteration window. A spread over too few points is "
               "not a spread." % (label, len(series),
                                  max(th["min_samples"], n_window),
                                  th["window_iterations"]))
    win = series[-n_window:]

    diffs = [b - a for a, b in zip(win, win[1:])]
    signs = [1 if d > 0 else -1 for d in diffs if d != 0]
    sign_changes = sum(1 for a, b in zip(signs, signs[1:]) if a != b)

    n = len(win)
    xs = list(range(n))
    mx, my = sum(xs) / n, sum(win) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in win)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, win))
    trend_frac = 0.0 if syy <= 0 or sxx <= 0 else (sxy * sxy) / (sxx * syy)

    if cm["status"] == "CONVERGED":
        state = "CONVERGED"
    elif sign_changes >= SIGN_CHANGES_MIN and trend_frac < TREND_FRAC_MAX:
        state = "CYCLING"
    else:
        state = "DRIFTING"

    return dict(state=state, label=label, artifact=dat_path,
                spread_pct=cm["peak_to_peak_pct"],
                spread_abs=cm["peak_to_peak_abs"],
                range_over_run=cm["run_range"],
                normaliser=cm["normaliser"],
                spread_pct_vs_mean=cm["peak_to_peak_pct_vs_mean"],
                print_resolution=cm["print_resolution"],
                sign_changes=sign_changes, trend_frac=trend_frac,
                n_samples=len(series), window_samples=n_window,
                thresholds=th, shared_status=cm["status"],
                shared_instrument="check_convergence.classify_monitor",
                window_values=win)


def classify_series_values(values, label, tmpdir):
    """Classify a DERIVED series by materialising it and calling the same path."""
    path = materialise_dat(list(range(CYCLE_INTERVAL,
                                      CYCLE_INTERVAL * (len(values) + 1),
                                      CYCLE_INTERVAL)),
                           values,
                           os.path.join(tmpdir, "%s.dat" % re.sub(r"\W", "_", label)))
    return classify_cycle(path, label)


# ---------------------------------------------------------------------------
# s.6.2 -- the detector must be SHOWN able to detect a cycle
# ---------------------------------------------------------------------------
def planted_cycle_control(base_values, label, tmpdir):
    """s.6.2, for a level and a quantity, BEFORE that level is classified.

    A cycle detector never shown able to detect a cycle is worth exactly as much
    as a zero from a blind reader.  Positive arm: a sinusoid at 2x the
    registered spread threshold, period 200 iterations -- must classify
    `CYCLING` or this comparator REFUSES at exit 2.  Negative arm: a clean
    monotone decaying series must NOT classify `CYCLING`.  Then the MEASURED
    DETECTION FLOOR at 1.0x, 0.5x, 0.25x, 0.125x, 0.0625x, which is quoted
    beside every `CONVERGED` reading -- a `CONVERGED` without it is an
    unqualified negative.
    """
    rng = max(base_values) - min(base_values)
    if rng <= 0:
        refuse("planted-cycle control for %s: the base series has zero range, so "
               "no amplitude can be expressed against it" % label)
    n = len(base_values)
    if n < CYCLE_MIN_SAMPLES:
        refuse("planted-cycle control for %s: %d base samples, fewer than the "
               "registered minimum %d" % (label, n, CYCLE_MIN_SAMPLES))

    def synth(amp_frac):
        """THE CYCLE IS PLANTED ONTO THIS LEVEL'S OWN SERIES, and that choice is
        load-bearing rather than incidental.

        Two simpler forms were tried and BOTH are wrong, so both are recorded:

          * `level + ramp + amp*sin(...)` -- the ramp dominates the window's
            linear trend, `trend_frac` goes above 0.25, and the POSITIVE ARM
            CLASSIFIES `DRIFTING`.  Measured here, not imagined: it failed this
            file's own selftest on first execution.
          * `level + amp*sin(...)` alone (K2d s.3.3b's form) -- the synthetic
            series' RUN RANGE *is* its own amplitude, so `spread_pct` reads
            ~100 % at EVERY planted amplitude and every fraction classifies
            `CYCLING`.  The "measured detection floor" would then report the
            smallest fraction tried, whatever it was, and could never fail.  A
            floor that cannot fail is not a measurement.

        Planting onto the real base fixes both: the run range is the base's,
        which is what the registered normaliser refers the spread to, and the
        window spread is ~2*amp because the base has plateaued there.  The floor
        is then a real number -- with the registered threshold at 0.02 % of
        range, a sinusoid of amplitude `f * 0.02 % * range` spans `f * 0.04 %`
        and is detected for f above 0.5.
        """
        # period 200 iterations == 4 samples at the registered 50-iteration
        # cadence.  The amplitude is a fraction of the registered spread
        # THRESHOLD expressed against the base series' own range-spanned, so the
        # floor is reported in the units the gate is written in.
        amp = amp_frac * (CYCLE_TOL_PCT / 100.0) * rng
        return [b + amp * math.sin(2 * math.pi * i / 4.0)
                for i, b in enumerate(base_values)]

    pos = classify_series_values(synth(2.0), "%s::planted-cycle+" % label, tmpdir)
    if pos["state"] != "CYCLING":
        refuse("PLANTED-CYCLE CONTROL FAILED (positive arm) for %s: a sinusoid "
               "planted at 2x the registered spread threshold, period 200 "
               "iterations, classified %r and not CYCLING. The detector cannot "
               "see the phenomenon P-K2f-1 predicts, so this comparator will not "
               "grade." % (label, pos["state"]))

    lo = min(base_values)
    clean = [lo + rng * math.exp(-3.0 * i / n) for i in range(n)]
    neg = classify_series_values(clean, "%s::planted-cycle-" % label, tmpdir)
    if neg["state"] == "CYCLING":
        refuse("PLANTED-CYCLE CONTROL FAILED (negative arm) for %s: a clean "
               "monotone decaying series classified CYCLING. A detector that "
               "calls everything a cycle is as useless as one that calls "
               "nothing." % label)

    floor = None
    ladder = {}
    for frac in FLOOR_FRACTIONS:
        st = classify_series_values(synth(frac), "%s::floor%g" % (label, frac),
                                    tmpdir)["state"]
        ladder["%gx" % frac] = st
        if st == "CYCLING":
            floor = frac
    return dict(positive_arm=pos["state"], negative_arm=neg["state"],
                detection_floor_frac_of_threshold=floor, floor_ladder=ladder,
                note=("the smallest planted amplitude still classified CYCLING, "
                      "as a fraction of the registered %g %% spread threshold; a "
                      "CONVERGED reading WITHOUT this figure is an unqualified "
                      "negative" % CYCLE_TOL_PCT))


# ---------------------------------------------------------------------------
# mesh gates -- s.5.4, carried from K2d whose limbs were sound
# ---------------------------------------------------------------------------
_GEOM_RE = re.compile(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions "
                      r"\(([\d ]+)\)")


def read_checkmesh(case_dir):
    """Everything the three checkMesh-derived gates need, or REFUSE.

    NEVER reads `blockMeshDict`.  The gate reads what was BUILT, not what was
    asked for.
    """
    path = os.path.join(case_dir, "log.checkMesh")
    if not os.path.isfile(path):
        refuse("%s has no log.checkMesh -- mesh quality and dimensionality are "
               "UNMEASURED, and unmeasured is not passing" % case_dir)
    with open(path, errors="replace") as fh:
        text = fh.read()
    prov_ok = ("-allGeometry" in text) and ("-allTopology" in text)
    n_failed, failed_lines = None, []
    for ln in text.splitlines():
        m = re.search(r"Failed (\d+) mesh check", ln)
        if m:
            n_failed = int(m.group(1))
        if ln.strip() == "Mesh OK." and n_failed is None:
            n_failed = 0
        if "***" in ln:
            failed_lines.append(ln.strip())
    gm = _GEOM_RE.search(text)
    # THE TRAILING-PERIOD TRAP, AND IT IS A MEASURED DEFECT INHERITED FROM
    # `analyse_k2d.py:193`, WHICH CARRIES THIS REGEX VERBATIM.
    # checkMesh prints
    #     Min volume = 0.0004687499981. Max volume = 0.0006015625022.
    # -- the value is followed by a SENTENCE PERIOD.  `([0-9.eE+-]+)` is greedy
    # over `.` and captures "0.0004687499981.", and `float()` of that raises
    # ValueError.  Not a refusal: an UNCAUGHT CRASH at exit 1, from a comparator
    # whose exit map reserves 1 for a failed selftest.
    #
    # K2d's 31 green arms never saw it BECAUSE EVERY ARM FED IT A SYNTHETIC LOG
    # THAT THE SAME AUTHOR HAD WRITTEN.  A selftest built only from synthetic
    # artifacts validates a reader against its author's idea of the artifact,
    # and both sides of that comparison share the misconception.  This one was
    # found the first time the comparator was pointed at a log OpenFOAM actually
    # wrote -- which is the whole argument for s.7 being a pre-freeze obligation.
    #
    # The repaired pattern cannot END on a `.`, so a sentence period stays out.
    mc = re.search(r"Min volume = ([-+0-9.eE]*[0-9])", text)
    return dict(path=path, provenance_full_set=prov_ok, n_failed=n_failed,
                failed_lines=failed_lines,
                geometric_line=gm.group(0) if gm else None,
                n_geometric=int(gm.group(1)) if gm else None,
                min_volume=float(mc.group(1)) if mc else None)


def gate_checkmesh(cm):
    """G-CHECKMESH, s.5.4 -- provenance limb, then verdict limb."""
    if not cm["provenance_full_set"]:
        return False, ("G-CHECKMESH PROVENANCE: %s does not evidence BOTH "
                       "-allGeometry and -allTopology. A log missing half the "
                       "checks is not evidence of a sound mesh, and G-3D reads "
                       "this same log." % cm["path"])
    if cm["n_failed"] is None:
        return False, ("G-CHECKMESH VERDICT: %s carries NO verdict line -- "
                       "neither `Mesh OK.` nor `Failed N mesh checks`. Mesh "
                       "quality is UNMEASURED, and unmeasured is not passing."
                       % cm["path"])
    if cm["n_failed"] > 0:
        untolerated = [ln for ln in cm["failed_lines"]
                       if not any(k.lower() in ln.lower() for k in MESHQ_TOLERANCE)]
        if untolerated:
            return False, ("G-CHECKMESH VERDICT: checkMesh -allGeometry "
                           "-allTopology FAILED %d check(s) with no registered "
                           "tolerance covering: %s. The mesh is REBUILT, or a "
                           "tolerance is registered with its justification "
                           "BEFORE the freeze -- the gate is never relaxed to "
                           "let a mesh through after the mesh has been seen."
                           % (cm["n_failed"], "; ".join(untolerated[:3])))
    return True, ("G-CHECKMESH PASS (full check set run, %d failed checks)"
                  % cm["n_failed"])


def read_patch_census(case_dir):
    """G-3D input: patch types from `constant/polyMesh/boundary` -- the BUILT
    mesh.  `blockMeshDict` is never read for this."""
    p = os.path.join(case_dir, "constant", "polyMesh", "boundary")
    if not os.path.isfile(p):
        refuse("%s has no constant/polyMesh/boundary" % case_dir)
    with open(p, errors="replace") as fh:
        text = fh.read()
    return {t: len(re.findall(r"type\s+%s\s*;" % t, text))
            for t in ("empty", "wedge", "patch", "wall", "symmetry",
                      "cyclic", "mappedWall")}


def gate_3d(cm, census):
    """G-3D, s.5.4.  T4e and the whole T23G2 line were 2D wedges.

    Reads the VERBATIM `Mesh has N geometric (non-empty/wedge) directions` line
    and NEVER the `solution (non-empty)` line, which reads 3 for a wedge.
    """
    if cm["n_geometric"] is None:
        return False, ("G-3D: no `Mesh has N geometric (non-empty/wedge) "
                       "directions` line in %s. Dimensionality UNMEASURED."
                       % cm["path"])
    if cm["n_geometric"] != 3:
        return False, ("G-3D: %r -- this mesh has %d geometric directions, not "
                       "3. It is NOT a 3D case."
                       % (cm["geometric_line"], cm["n_geometric"]))
    bad = {k: v for k, v in census.items() if k in ("empty", "wedge") and v}
    if bad:
        return False, ("G-3D: the BUILT boundary carries %s. A wedge mesh "
                       "reports 3 SOLUTION directions while being 2D; this gate "
                       "reads the GEOMETRIC line and the patch census, never "
                       "blockMeshDict."
                       % ", ".join("%d %s patch(es)" % (v, k)
                                   for k, v in bad.items()))
    return True, "G-3D CONFIRMED: %r, no empty/wedge patches" % cm["geometric_line"]


def gate_mincell(case_dir, features=NAMED_FEATURES):
    """G-MINCELL, s.5.4 -- minimum cell dimension per NAMED feature vs the floor.

    cfd's M6 finding: a cusped trailing edge passed BOTH check sets and still
    destroyed the rung.  A geometry limb independent of checkMesh is required.
    """
    p = os.path.join(case_dir, "MINCELL.json")
    if not os.path.isfile(p):
        refuse("%s has no MINCELL.json -- the per-feature minimum cell dimension "
               "is UNMEASURED, and unmeasured is not passing. build_k2f.py "
               "writes it at build time." % case_dir)
    with open(p) as fh:
        got = json.load(fh)
    missing = [f for f in features if f not in got]
    if missing:
        return False, ("G-MINCELL: no measurement for named feature(s): %s"
                       % ", ".join(missing)), got
    under = {f: got[f] for f in features if float(got[f]) < MINCELL_FLOOR_M}
    if under:
        return False, ("G-MINCELL: feature(s) below the registered %.1f mm floor: "
                       "%s" % (MINCELL_FLOOR_M * 1e3,
                               ", ".join("%s = %.4g m" % (k, v)
                                         for k, v in under.items()))), got
    return True, ("G-MINCELL PASS: every named feature >= %.1f mm (worst %.4g m)"
                  % (MINCELL_FLOOR_M * 1e3,
                     min(float(got[f]) for f in features))), got


def built_cell_count(case_dir):
    """Cell count read from the BUILT polyMesh.  Never from a target."""
    owner = os.path.join(case_dir, "constant", "polyMesh", "owner")
    if not os.path.isfile(owner):
        refuse("%s has no constant/polyMesh/owner" % case_dir)
    with open(owner, "rb") as fh:
        head = fh.read(4096).decode("utf-8", "replace")
    m = re.search(r"nCells:\s*(\d+)", head)
    if not m:
        refuse("%s/constant/polyMesh/owner carries no nCells in its header note"
               % case_dir)
    return int(m.group(1))


def gate_meshsim(counts):
    """G-MESHSIM, s.1.  A ladder graded on intended counts grades an intention."""
    n1, n2, n3 = (counts[L] for L in LEVELS)
    r_a, r_b = n2 / n1, n3 / n2
    ok = all(MESHSIM_LO <= r <= MESHSIM_HI for r in (r_a, r_b))
    msg = ("G-MESHSIM %s: BUILT counts %d / %d / %d, actual steps %.4f / %.4f "
           "(window [%.4f, %.4f] = 3.375 +- 5 %%), implied r = %.4f / %.4f"
           % ("PASS" if ok else "FAIL", n1, n2, n3, r_a, r_b,
              MESHSIM_LO, MESHSIM_HI, r_a ** (1 / DIM), r_b ** (1 / DIM)))
    return ok, msg, dict(built=dict(counts), step_21=r_a, step_32=r_b,
                         r_21=r_a ** (1 / DIM), r_32=r_b ** (1 / DIM))


# ---------------------------------------------------------------------------
# s.9.2 -- the completion rule, through the rung's ONE instrument
# ---------------------------------------------------------------------------
def gate_completion(case_dir):
    """Standing rule 4, all six clauses, by CALLING `mark_done_k2f.check`.

    Not reimplemented.  There is one implementation of the completion rule for
    this rung and the comparator and the launcher both go through it.
    """
    done, why = MD.check(case_dir)
    if done is None:
        refuse("COMPLETION INSTRUMENT REFUSED for %s: %s"
               % (case_dir, "; ".join(why)))
    if not done:
        return False, ("STRICT COMPLETION RULE: %s is NOT DONE -- %s"
                       % (os.path.basename(case_dir), "; ".join(why)))
    return True, ("STRICT COMPLETION RULE: %s DONE, all six clauses "
                  "(mark_done_k2f.check)" % os.path.basename(case_dir))


# ---------------------------------------------------------------------------
# s.0.3 -- convergence-STATE INVARIANCE across the ladder
# ---------------------------------------------------------------------------
def gate_stateinv(states_by_quantity):
    """G-STATEINV, registration s.0.3.

    **A triple whose levels differ in CONVERGENCE STATE is invalid IN PRINCIPLE,
    not merely by rule.**  A Roache triple assumes the three values differ by
    DISCRETISATION ERROR.  Three levels that differ in whether they reached a
    steady state at all are not solving the same problem in the same regime: the
    coarse level converges to a steady state the fine levels say does not exist,
    and the inter-level differences then measure a MIXTURE of discretisation
    error and convergence state.  K2d's own residual histories show it -- L1 to
    9.8e-10 and flat, L2 floored at 1.75e-04 and limit-cycling.

    BOTH GROUNDS ARE KEPT AND BOTH ARE PRINTED.  Standing rule 5 clause (1) is
    the AUTHORITY -- any level not iteratively converged voids every row -- and
    is not a lane's to retire.  This limb is the INDEPENDENT MECHANISM by which
    the same answer follows.  It is stated separately because a record that
    prints only the rule teaches nothing about why the rule is right here.

    NOTE HONESTLY: this limb is never the SOLE cause of a NOT A RESULT.  Any
    state split necessarily contains a non-CONVERGED level, which rule 5 clause
    (1) has already voided.  Its work is in the RECORD, not in the verdict.
    """
    split = {}
    for q, per_level in states_by_quantity.items():
        distinct = sorted(set(per_level.values()))
        if len(distinct) > 1:
            split[q] = dict(states=dict(per_level), distinct=distinct)
    if not split:
        return True, ("G-STATEINV: every level reads the same convergence state "
                      "on every gated quantity; the triple is admissible in "
                      "principle"), {}
    detail = "; ".join(
        "%s: %s" % (q, ", ".join("%s=%s" % (lv, st)
                                 for lv, st in v["states"].items()))
        for q, v in split.items())
    return False, ("G-STATEINV (s.0.3): the ladder SPLITS on convergence state "
                   "-- %s. The three values do not differ by discretisation "
                   "error alone: a level that reached a steady state and a level "
                   "that did not are not solving the same problem in the same "
                   "regime, so the inter-level differences measure a MIXTURE of "
                   "discretisation error and convergence state. The triple is "
                   "INVALID IN PRINCIPLE. Standing rule 5 clause (1) reaches the "
                   "same verdict on its own authority and is the binding ground."
                   % detail), split


# ---------------------------------------------------------------------------
# rule 5, in its order, with every primitive shared
# ---------------------------------------------------------------------------
def grade_row(row_id, levels, admitted_why, order_band=(ORDER_LO, ORDER_HI)):
    """Standing rule 5, in its order, ONE-WAY (s.5.2).

    `levels` is coarse-first `[{name, cells, value}, ...]`.
    `admitted_why` is a list of reasons the row is already NOT A RESULT from the
    admission steps; if it is non-empty the row is voided BEFORE any grid claim,
    which is rule 5 clause (1).

    The arithmetic is `RT.all_triples`; monotonicity is `RT.monotone`; the
    NOT-A-RESULT state set is `RT.NOT_A_RESULT_STATES`; and the band comparison
    itself is `RT.band_verdict` -- applied to the OBSERVED ORDER, because that is
    what K2f registers at s.5.3.  See the module docstring for why
    `RT.grade_ladder` is not the entry point and how this ordering is checked
    against it.
    """
    meta = GRADED_ROWS[row_id]
    base = dict(row=row_id, quantity=meta["quantity"], unit=meta["unit"],
                derived=meta["derived"], derivation=meta["why"], dim=DIM, fs=FS,
                order_band=list(order_band),
                levels=[dict(lv) for lv in levels],
                values=[lv["value"] for lv in levels],
                cells=[lv["cells"] for lv in levels],
                annotations=[], gci_pct=None, gci_abs=None, order=None)

    # ---- (1) admission: not iteratively converged / not plateaued ----------
    if admitted_why:
        base.update(verdict="NOT A RESULT", band_verdict=None,
                    triple_state=None,
                    why="; ".join(admitted_why))
        return base

    triples = RT.all_triples(levels, DIM, fs=FS)
    finest = triples[-1]
    base["triples"] = [RT._triple_public(t) for t in triples]
    base["orders"] = [t.get("order") for t in triples]
    base["states"] = [t["state"] for t in triples]
    base["triple_state"] = finest["state"]
    base["monotone"] = RT.monotone(finest)

    # The band verdict is computed FIRST and UNCONDITIONALLY wherever an order
    # exists, so the one-way property of the gate is CHECKABLE rather than
    # asserted: the final verdict must be this one or NOT A RESULT.
    bv = None
    if finest.get("order") is not None:
        bv, _bounds = RT.band_verdict(finest["order"], order_band)
    base["band_verdict"] = bv

    # ---- (2) the triple itself ---------------------------------------------
    if finest["state"] in RT.NOT_A_RESULT_STATES:
        base.update(verdict="NOT A RESULT", order=finest.get("order"),
                    why=("finest triple %s is %s at dim = %d; the value, BOTH "
                         "triples and BOTH orders are printed beside it and NO "
                         "GCI is quoted"
                         % (finest["levels"], finest["state"], DIM)))
        return _seal_oneway(base, bv)
    if not RT.monotone(finest):
        base.update(verdict="NOT A RESULT", order=finest.get("order"),
                    why=("the three values are not monotone; a GCI may NEVER be "
                         "quoted here (standing rule 5)"))
        return _seal_oneway(base, bv)

    # ---- (3) CONVERGING: the registered ORDER band, GCI printed -------------
    p = finest["order"]
    base["order"] = p
    base["gci_pct"] = finest["GCI_pct"]
    base["gci_abs"] = finest["GCI_abs"]
    base["richardson"] = finest["richardson"]
    if bv == "PASS" and p < SUBFIRST:
        base["annotations"].append(
            "A-SUBFIRST: p = %.4f < 1.0 on a nominally second-order scheme. "
            "Sub-first-order convergence indicates an unresolved or "
            "STRUCTURALLY-DOMINANT error source -- an unresolved feature, a "
            "discontinuity, or mesh defects that do not dilute under refinement "
            "-- and NOT merely slow convergence. This PASS is inside the "
            "registered band and stands; it may NOT be cited as evidence of "
            "asymptotic convergence." % p)
    if bv == "PASS":
        base["annotations"].append(
            "The registered band (%.1f, %.1f) is WIDER than this lab's usual "
            "(1.5, 2.5) -- s.5.3. A PASS inside it is a WEAKER claim and may NOT "
            "be cited as second-order accuracy." % (ORDER_LO, ORDER_HI))
    base.update(verdict=bv,
                why=("finest triple %s CONVERGING at dim = %d, observed order "
                     "%.4f %s the registered band (%.1f, %.1f), GCI %.4f %% = "
                     "%.6g absolute at Fs = %s"
                     % (finest["levels"], DIM, p,
                        "inside" if bv == "PASS" else "OUTSIDE",
                        ORDER_LO, ORDER_HI, finest["GCI_pct"],
                        finest["GCI_abs"], FS)))
    return _seal_oneway(base, bv)


def _seal_oneway(row, bv):
    """The gate is ONE-WAY: it may only turn a PASS or GATE FAIL INTO a
    NOT A RESULT, never the reverse.  `raise`, never `assert`, so that `-O`
    cannot strip the check."""
    if row["verdict"] not in (bv, "NOT A RESULT"):
        raise RuntimeError(
            "ONE-WAY VIOLATION in row %s: band verdict %r became %r. The gate "
            "may only turn a PASS or GATE FAIL INTO NOT A RESULT."
            % (row["row"], bv, row["verdict"]))
    if row["verdict"] not in RT.VERDICTS:
        raise RuntimeError("row %s emitted %r, which is not in the fixed verdict "
                           "vocabulary %s" % (row["row"], row["verdict"],
                                              RT.VERDICTS))
    return row


# ---------------------------------------------------------------------------
# s.4.1 -- S-ONSET, the registered finding
# ---------------------------------------------------------------------------
def s_onset(cycle_states, cycle_controls, cells, decomp_control=None):
    """s.4.1.  A per-level convergence-state census, printed for EVERY level
    whatever the verdicts are, in the registered words.

    S-ONSET GRADES NOTHING AND MOVES NO VERDICT.  It is the registered ground
    for a transient successor under its own pre-registration and its own cost,
    and it is nothing else.  It makes NO claim about the physical unsteadiness
    of a real data centre, about model-form error, or about any resolution not
    run.
    """
    rows = []
    for lv in LEVELS:
        for q in CYCLE_QUANTITIES:
            st = cycle_states.get(lv, {}).get(q)
            if st is None:
                continue
            ctl = cycle_controls.get(lv, {}).get(q, {})
            rows.append(dict(
                level=lv, cells=cells.get(lv), quantity=q, state=st["state"],
                spread_pct_of_range=st["spread_pct"],
                range_spanned=st["range_over_run"],
                sign_changes=st["sign_changes"], trend_frac=st["trend_frac"],
                n_samples=st["n_samples"],
                print_resolution=st["print_resolution"],
                detection_floor_frac_of_threshold=ctl.get(
                    "detection_floor_frac_of_threshold"),
                statement=("the steady kOmegaSST treatment of the K2a module "
                           "reads %s at %s cells" % (st["state"], cells.get(lv)))))
    out = dict(rows=rows, decomp_control=decomp_control or "NOT RUN",
               grades="NOTHING",
               scope=("a statement about a STEADY SOLVER's behaviour on three "
                      "meshes. It is NOT a measurement of physical unsteadiness "
                      "in a data centre and no K2f sentence may present it as "
                      "one (s.14)."))
    if (decomp_control or "NOT RUN") == "NOT RUN":
        out["decomp_caveat"] = (
            "C-DECOMP was NOT RUN, so S-ONSET MAY NOT be cited as establishing "
            "that the cycle is a property of the case rather than of the "
            "parallel path (s.18.3). The gap is LABELLED here, not left for a "
            "reader to infer.")
    return out


# ---------------------------------------------------------------------------
# s.15 -- the freeze block
# ---------------------------------------------------------------------------
def verify_freeze():
    """s.15: the comparator verifies each frozen file IS the file that ran by
    hashing it against the committed blob, and REFUSES rather than grading if a
    digest fails to reproduce.

    The registration's freeze block is currently EMPTY (`*pending*`), which is
    the correct pre-freeze state.  This limb REPORTS that plainly and does not
    pretend to a verification it cannot do -- and it REFUSES the moment a digest
    is present and does not reproduce.
    """
    reg = os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder",
                       "K2f_PREREGISTRATION.md")
    if not os.path.isfile(reg):
        refuse("the registration %s is absent; there is no frozen gate to grade "
               "against" % reg)
    text = open(reg, errors="replace").read()
    # EVERY FILE s.15 PINS, NOT JUST THIS RUNG'S OWN FOUR.
    # s.15 also pins `scripts/roache_triple.py`, and the first form of this limb
    # did not check it.  MEASURED, 2026-09-11: the draft pinned
    # 78e56a3b... while the file on disk was 23afaee3... -- the verification team
    # had repaired the shared instrument the same hour.  **The freeze block would
    # have pinned a blob that is not the file that runs**, which is precisely the
    # thing s.15 exists to make impossible, and the comparator would not have
    # noticed because it was only checking its own directory.
    # A shared instrument moves under a rung without the rung being told; that is
    # what makes it shared, and it is why the digest must be checked at GRADE
    # time and not only at freeze time.
    PINS = {"build_k2f.py": HERE, "analyse_k2f.py": HERE,
            "mark_done_k2f.py": HERE, "launch_k2f.sh": HERE,
            "scripts/roache_triple.py": REPO}
    pinned, where = {}, {}
    for name, base in PINS.items():
        m = re.search(r"\|\s*`%s`\s*\|\s*([^|]+?)\s*\|" % re.escape(name), text)
        if m:
            pinned[name] = m.group(1).strip().strip("`").split("`")[0].strip()
            where[name] = os.path.join(base, os.path.basename(name)
                                       if base is HERE else name)
    # A PIN IS A 40-HEX BLOB AND NOTHING ELSE.  The first form of this test asked
    # whether the cell read exactly "pending" -- and s.15's `launch_k2f.sh` row
    # reads "*pending -- **pinned in this rung**, unlike K2d where it was not*",
    # so the test fell through to the digest branch and REFUSED the whole
    # comparator on an UNFROZEN document.  Found by execution, in this file's own
    # A-DRIVE arm.  The repaired test asks the only question that has an answer:
    # is this cell a blob digest?
    _BLOB = re.compile(r"^[0-9a-f]{40}$")
    unfrozen = [k for k, v in pinned.items() if not _BLOB.match(v.strip())]
    if len(unfrozen) == len(pinned) and pinned:
        return dict(state="NOT FROZEN", pinned=pinned,
                    note=("registration s.15 carries NO blob digest for any "
                          "grading-path file. This is the correct PRE-FREEZE state. "
                          "NO VERDICT PRODUCED BY THIS RUN IS A REGISTERED "
                          "MEASUREMENT OF THE RUNG."))
    import subprocess
    bad = {}
    for name, want in pinned.items():
        if not _BLOB.match(want.strip()):
            bad[name] = ("s.15 carries %r, which is not a 40-hex blob digest. A "
                         "freeze block that names a file without pinning it pins "
                         "nothing." % want[:60])
            continue
        path = where[name]
        if not os.path.isfile(path):
            bad[name] = "pinned to %s but the file is absent" % want
            continue
        got = subprocess.run(["git", "hash-object", path], cwd=REPO,
                             capture_output=True, text=True).stdout.strip()
        if got != want:
            bad[name] = "pinned blob %s, on disk %s" % (want, got)
    if bad:
        refuse("FREEZE DIGEST MISMATCH -- the file that would grade is NOT the "
               "file that was frozen: %s. The comparator refuses rather than "
               "grading (s.15)."
               % "; ".join("%s: %s" % kv for kv in bad.items()))
    return dict(state="FROZEN AND VERIFIED", pinned=pinned)


# ---------------------------------------------------------------------------
# THE DRIVE PATH.  main() -> grade() -> every gate above.
# ---------------------------------------------------------------------------
def grade(root, out_json=None):
    """Point this at a case root and get a verdict.  `A-DRIVE`, s.7.

    THIS IS THE FUNCTION K2d DID NOT HAVE.  Returns (exit_code, report).
    A refusal comes back NAMED -- identifying the limb and the missing input --
    never as a generic "nothing to grade".
    """
    report = dict(rung="K2f", root=os.path.abspath(root), dim=DIM,
                  registration="docs/campaigns/F14-cooling-ladder/"
                               "K2f_PREREGISTRATION.md",
                  levels={}, rows=[], refusals=[])
    report["freeze"] = verify_freeze()
    report["end_rack_mapping"] = (
        "registration s.5.1 row G3 names `T_in,1` in a ONE-BASED rack numbering; "
        "the builder writes rack0_in..rack%d_in, ZERO-BASED. The row is graded on "
        "builder index %d -- the rack at x in [0.6, 1.2], against the row's outer "
        "end, which is the rack the registration's own parenthetical identifies."
        % (N_RACKS - 1, END_RACK_INDEX))
    report["G4_control_volume"] = (
        "registration s.5.1 registers G4 as volume-averaged T over `the cold "
        "aisle` and NOWHERE DEFINES THE VOLUME. The comparator grades the "
        "`caZone` cellZone that build_k2f.py writes, which is the exact parallel "
        "of the registered HA_BOX. THAT BOX IS A PROPOSAL AND NOT A REGISTERED "
        "DEFINITION; until s.3 fixes it, no G4 verdict from this comparator is a "
        "registered measurement.")

    # ---- per-level admission ----------------------------------------------
    cells, cycle_states, cycle_controls, plant_controls = {}, {}, {}, {}
    admitted_why = []
    tmpdir = tempfile.mkdtemp(prefix="k2f_grade_")
    try:
        for lv in LEVELS:
            cd = os.path.join(root, lv)
            L = dict(case=cd)
            report["levels"][lv] = L
            if not os.path.isdir(cd):
                refuse("A-DRIVE NAMED REFUSAL: level %s has no case directory at "
                       "%s. The ladder is incomplete and a Roache triple needs "
                       "all three levels. (This is the NAMED refusal registration "
                       "s.7 direction 2 requires -- it identifies the missing "
                       "input, not merely that there is nothing to grade.)"
                       % (lv, cd))

            ok, msg = gate_completion(cd)
            L["completion"] = dict(ok=ok, why=msg)
            if not ok:
                admitted_why.append(msg)

            cm = read_checkmesh(cd)
            ok, msg = gate_checkmesh(cm)
            L["checkmesh"] = dict(ok=ok, why=msg, n_failed=cm["n_failed"])
            if not ok:
                admitted_why.append(msg)

            census = read_patch_census(cd)
            ok, msg = gate_3d(cm, census)
            L["g3d"] = dict(ok=ok, why=msg, census=census)
            if not ok:
                admitted_why.append(msg)

            ok, msg, mm = gate_mincell(cd)
            L["mincell"] = dict(ok=ok, why=msg,
                                worst=min(float(mm[f]) for f in NAMED_FEATURES
                                          if f in mm) if mm else None)
            if not ok:
                admitted_why.append(msg)

            cells[lv] = built_cell_count(cd)
            L["cells"] = cells[lv]

            ok, msg, inp = gate_input(cd)          # A-INPUT; refuses if absent
            L["a_input"] = dict(ok=ok, why=msg,
                                series={k: dict(n_samples=v["n_samples"],
                                                last=v["last"],
                                                print_resolution=v["print_resolution"],
                                                run_range=v["run_range"],
                                                path=v["path"])
                                        for k, v in inp.items()})

            # standing rule 3, on the READER, on this level's own artifacts
            plant_controls[lv] = {n: planted_zero_control(cd, n)
                                  for n in ("U_ha", "T_ca",
                                            "T_in_%d" % END_RACK_INDEX)}
            L["planted_zero"] = {n: dict(passed=p["passed"], planted=p["planted"],
                                         reader_delta=p["reader_delta"],
                                         gate_path_delta=p["gate_path_delta"],
                                         artifact=p["artifact"])
                                 for n, p in plant_controls[lv].items()}

            # the derived series, built from the primitives
            tin = {}
            for i in range(N_RACKS):
                its, vals, _raw = read_dat_series(series_path(cd, "T_in_%d" % i))
                tin[i] = (its, vals)
            n = min(len(v) for _t, v in tin.values())
            t_in_max = [max(tin[i][1][j] for i in range(N_RACKS)) for j in range(n)]
            theta_max = [(v - T_SUP) / DT_RACK for v in t_in_max]
            L["derived"] = dict(
                T_in_max_last=t_in_max[-1], theta_max_last=theta_max[-1],
                note=("T_in,max and theta_max have NO OpenFOAM producer and need "
                      "none: the first is a max over four PATCH AVERAGES (not "
                      "over faces, which is what a function object's `max` would "
                      "return) and the second is an affine map of it with both "
                      "constants registered at s.2. Registration s.3 lists both "
                      "as `written by in-pass functions entries` and BOTH ARE "
                      "DERIVED -- reported as a finding."))

            lvdir = os.path.join(tmpdir, lv)
            os.makedirs(lvdir, exist_ok=True)

            # s.6.2 BEFORE any level is classified: the detector must be shown
            # able to detect a cycle, on THIS level's own data.
            cycle_controls[lv] = {
                "T_in,max": planted_cycle_control(t_in_max, "%s::T_in,max" % lv, lvdir),
                "U_ha": planted_cycle_control(
                    read_dat_series(series_path(cd, "U_ha"))[1],
                    "%s::U_ha" % lv, lvdir),
            }
            L["planted_cycle"] = cycle_controls[lv]

            cycle_states[lv] = {
                "T_in,max": classify_series_values(t_in_max, "%s::T_in,max" % lv,
                                                   lvdir),
                "U_ha": classify_cycle(series_path(cd, "U_ha"), "%s::U_ha" % lv),
            }
            L["g_cycle"] = {q: {k: v for k, v in st.items()
                                if k != "window_values"}
                            for q, st in cycle_states[lv].items()}

        # ---- ladder-wide admission -----------------------------------------
        ok, msg, ms = gate_meshsim(cells)
        report["meshsim"] = dict(ok=ok, why=msg, detail=ms)
        if not ok:
            admitted_why.append(msg)

        # ---- G-CYCLE, s.5.2 step 2 ------------------------------------------
        bad_cycle = [(lv, q, cycle_states[lv][q]["state"])
                     for lv in LEVELS for q in CYCLE_QUANTITIES
                     if cycle_states[lv][q]["state"] != "CONVERGED"]
        if bad_cycle:
            admitted_why.append(
                "G-CYCLE (standing rule 5 clause (1), s.5.2 step 2): %s. Any "
                "level not CONVERGED on either gated quantity voids EVERY graded "
                "row. This is not a lane's to retire and not this comparator's to "
                "soften: the verdict is NOT A RESULT, in those words."
                % "; ".join("%s %s reads %s" % t for t in bad_cycle))

        # ---- G-STATEINV, s.0.3 ----------------------------------------------
        ok, msg, split = gate_stateinv(
            {q: {lv: cycle_states[lv][q]["state"] for lv in LEVELS}
             for q in CYCLE_QUANTITIES})
        report["stateinv"] = dict(ok=ok, why=msg, split=split)
        if not ok:
            admitted_why.append(msg)

        # ---- the graded rows -------------------------------------------------
        def lvl(vals):
            return [dict(name=lv, cells=cells[lv], value=vals[lv]) for lv in LEVELS]

        vals_g1 = {lv: report["levels"][lv]["derived"]["T_in_max_last"] for lv in LEVELS}
        vals_g2 = {lv: report["levels"][lv]["derived"]["theta_max_last"] for lv in LEVELS}
        vals_g3 = {lv: report["levels"][lv]["a_input"]["series"]
                   ["T_in_%d" % END_RACK_INDEX]["last"] for lv in LEVELS}
        vals_g4 = {lv: report["levels"][lv]["a_input"]["series"]["T_ca"]["last"]
                   for lv in LEVELS}

        for rid, vals in (("G1", vals_g1), ("G2", vals_g2),
                          ("G3", vals_g3), ("G4", vals_g4)):
            report["rows"].append(grade_row(rid, lvl(vals), admitted_why))

        report["s_onset"] = s_onset(cycle_states, cycle_controls, cells)
        report["verdicts"] = {r["row"]: r["verdict"] for r in report["rows"]}
        code = EXIT_OK
    except Refuse as e:
        report["refusals"].append(str(e))
        report["verdicts"] = {}
        code = EXIT_REFUSE
    except RuntimeError:
        # the one-way seal and the verdict-vocabulary check.  These must stay
        # LOUD: a structural violation is not something to report as a refusal.
        raise
    except Exception as e:                                  # noqa: BLE001
        # A LIMB THAT CRASHED IS NOT A LIMB THAT REFUSED.  An uncaught exception
        # leaves through the interpreter at exit 1 -- which this rung's exit map
        # (s.9.5) reserves for a FAILED SELFTEST -- and a reader of the exit code
        # alone would call it a failed selftest rather than an unreadable
        # artifact.  It is converted to a NAMED refusal that identifies the limb,
        # and the exit code becomes 2.  Measured: `read_checkmesh` did exactly
        # this on the first REAL log it was pointed at.
        import traceback
        tb = traceback.extract_tb(sys.exc_info()[2])
        limb = tb[-1].name if tb else "?"
        report["refusals"].append(
            "LIMB CRASHED RATHER THAN REFUSED: %s raised %s: %s (at %s:%d). The "
            "comparator converts this to a NAMED refusal at exit 2 -- an uncaught "
            "exception would leave at exit 1, which s.9.5 reserves for a failed "
            "selftest, and a reader of the exit code alone would misread it."
            % (limb, type(e).__name__, e,
               os.path.basename(tb[-1].filename) if tb else "?",
               tb[-1].lineno if tb else 0))
        report["verdicts"] = {}
        code = EXIT_REFUSE
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if out_json:
        with open(out_json, "w") as fh:
            json.dump(report, fh, indent=1, sort_keys=True, default=str)
    return code, report


def print_report(report, code):
    """stdout, s.9.5.  THE EXIT CODE DOES NOT CARRY THE VERDICT."""
    print("=" * 78)
    print("K2f COMPARATOR -- %s" % report["root"])
    print("registration: %s" % report["registration"])
    fz = report.get("freeze", {})
    print("freeze: %s -- %s" % (fz.get("state"), fz.get("note", "")))
    print("=" * 78)
    if report["refusals"]:
        for r in report["refusals"]:
            print("\nREFUSED (exit 2): %s" % r)
        print("\nNOTHING WAS GRADED. No verdict is produced by a refusal, and no "
              "record may read one from the exit code.")
        return
    print("\n-- admission --")
    print("  %s" % report["meshsim"]["why"])
    print("  %s" % report["stateinv"]["why"])
    for lv in LEVELS:
        L = report["levels"][lv]
        print("  %s: %s" % (lv, L["completion"]["why"]))
        print("      %s" % L["checkmesh"]["why"])
        print("      %s" % L["g3d"]["why"])
        print("      %s" % L["mincell"]["why"])
        print("      %s" % L["a_input"]["why"])
        for n, p in L["planted_zero"].items():
            print("      planted-zero %s: passed=%s reader_delta=%.6e "
                  "gate_path_delta=%.6e" % (n, p["passed"], p["reader_delta"],
                                            p["gate_path_delta"]))
    print("\n-- S-ONSET (s.4.1): grades nothing, moves no verdict --")
    for r in report["s_onset"]["rows"]:
        print("  %-8s %-9s %-10s spread %.6f %% of range %.6g | signs %d | "
              "trend %.3f | n %d | detection floor %s x threshold"
              % (r["level"], r["quantity"], r["state"],
                 r["spread_pct_of_range"], r["range_spanned"],
                 r["sign_changes"], r["trend_frac"], r["n_samples"],
                 r["detection_floor_frac_of_threshold"]))
        print("           %s" % r["statement"])
    print("  decomp_control: %s" % report["s_onset"]["decomp_control"])
    if "decomp_caveat" in report["s_onset"]:
        print("  %s" % report["s_onset"]["decomp_caveat"])
    print("\n-- GRADED ROWS --")
    for r in report["rows"]:
        print("  %s  %-12s  %-14s  value %s" %
              (r["row"], r["quantity"], r["verdict"],
               ("%.8g" % r["values"][-1]) if r["values"] else "n/a"))
        print("      cells %s  values %s" % (r["cells"],
                                             ["%.8g" % v for v in r["values"]]))
        if r.get("orders"):
            print("      triples %s  orders %s" % (r["states"], r["orders"]))
        if r.get("gci_pct") is not None:
            print("      GCI %.4f %% = %.6g abs at Fs = %s, dim = %d"
                  % (r["gci_pct"], r["gci_abs"], FS, DIM))
        print("      %s" % r["why"])
        for a in r["annotations"]:
            print("      ANNOTATION: %s" % a)
    print("\n-- notes carried on every run --")
    print("  %s" % report["end_rack_mapping"])
    print("  %s" % report["G4_control_volume"])
    print("\nexit=%d  -- THE EXIT CODE DOES NOT CARRY THE VERDICT (s.9.5)." % code)


# ---------------------------------------------------------------------------
# the wiring audit -- a freeze verifies BYTES, never that anything CALLS them
# ---------------------------------------------------------------------------
GATE_FUNCTIONS = (
    "verify_freeze", "gate_completion", "read_checkmesh", "gate_checkmesh",
    "read_patch_census", "gate_3d", "gate_mincell", "built_cell_count",
    "gate_meshsim", "gate_input", "series_path", "read_dat_series",
    "resolve_unique", "materialise_dat", "planted_zero_control",
    "assert_registered_thresholds", "classify_cycle", "classify_series_values",
    "planted_cycle_control", "gate_stateinv", "grade_row", "_seal_oneway",
    "s_onset", "grade", "print_report",
)


def wiring_audit(path=None):
    """Parse THIS FILE'S AST, walk the call graph from `main`, and report every
    registered gate function that is NOT reachable from it.

    THE DEFECT THIS EXISTS FOR, MEASURED RATHER THAN IMAGINED.  `analyse_k2d.py`
    was frozen with 31 green selftest arms and a `main()` that graded nothing:
    `read_checkmesh`, `read_patch_census`, `gate_mincell` and `built_cell_count`
    each took a `case_dir` that `main()` never supplied.  A freeze verifies BYTES
    and never verifies that anything CALLS them -- three instruments in one week
    were perfectly frozen with no executable call site.

    STATED LIMITATION, AND IT IS STATED BECAUSE AN UNANNOTATED ONE IS WORSE THAN
    AN ANNOTATED ONE -- THIS INSTRUMENT'S WHOLE CLAIM IS THAT IT KNOWS WHAT IS
    REACHABLE.  This audit resolves call targets **by name, within one module**.
    It does not do type inference and cannot follow a call through an alias, a
    dict of handlers, a decorator or `getattr`.

    THE DEFECT THAT WAS IN ITS FIRST FORM, FOUND BY THE HEAT-TRANSFER SUPERVISOR
    IN THEIR SECTION 3 DIFF READ AND REPAIRED HERE.  The first form resolved
    `ast.Attribute` calls as `f.attr`, so ANY method call whose attribute name
    happened to match a registered gate function marked that gate REACHABLE
    WITHOUT IT EVER BEING CALLED -- a `self.grade()` or a `x.built_cell_count()`
    anywhere in the file would have silenced the audit for that gate.  **For an
    audit whose entire purpose is to catch gates that nothing calls, a
    false-REACHABLE is the dangerous direction: it is precisely the failure mode
    the audit exists to prevent, reintroduced one level down.**  The risk was low
    in this flat module-level file, and NOTHING ENFORCED THAT it stay flat.

    Repaired in both directions:
      * only `ast.Name` calls resolve, so reachability now errs toward
        FALSE-UNREACHABLE -- the direction that fails loudly rather than
        quietly.  A gate reached only through an attribute is reported as
        unreachable and must be called by bare name or added deliberately;
      * and a COLLISION ARM asserts that no `GATE_FUNCTIONS` name appears as an
        attribute anywhere in the file, so the assumption the first form made
        silently is now a checked precondition rather than a hope.

    Returns (ok, unreachable[], reached[], collisions[]).
    """
    path = path or os.path.abspath(__file__)
    tree = ast.parse(open(path).read(), filename=path)
    calls, defined, attrs = {}, set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute):
            attrs.add(node.attr)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defined.add(node.name)
            names = set()
            for sub in ast.walk(node):
                # ONLY a bare-name call resolves.  See the limitation above.
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                    names.add(sub.func.id)
            calls[node.name] = names
    reached, stack = set(), ["main"]
    while stack:
        cur = stack.pop()
        if cur in reached:
            continue
        reached.add(cur)
        stack.extend(n for n in calls.get(cur, ()) if n in defined)
    unreachable = sorted(f for f in GATE_FUNCTIONS if f not in reached)
    collisions = sorted(set(GATE_FUNCTIONS) & attrs)
    return ((not unreachable) and not collisions), unreachable, \
        sorted(reached & set(GATE_FUNCTIONS)), collisions


# ---------------------------------------------------------------------------
# the cross-check: reproduce a PUBLISHED triple before trusting the instrument
# ---------------------------------------------------------------------------
XCHECK = dict(
    source=("verification/runs/T-family/T23G2R_runs/"
            "T23G2R_COMPARATOR_STDOUT.txt:125"),
    cells=(40320, 90720, 204120), dim=2,
    values=(53.58204022, 52.94243232, 52.51458586),
    order=0.9917, gci_pct=2.0576, state="CONVERGING")


def cross_check(verbose=True):
    """Reproduce T23G2R's published Q4 triple EXACTLY through `RT`.

    CLAUDE.md rule 6: a citation that sits inside an executable check is the only
    kind that cannot rot quietly.  K2d did this same cross-check against this
    same published row; it is repeated here because an instrument is trusted
    after it reproduces a number somebody else published, not before.
    """
    t = RT.triple_from_cells(XCHECK["values"][0], XCHECK["values"][1],
                             XCHECK["values"][2],
                             XCHECK["cells"][0], XCHECK["cells"][1],
                             XCHECK["cells"][2], XCHECK["dim"], fs=RT.FS)
    got = dict(state=t["state"], order=round(t["order"], 4),
               gci_pct=round(t["GCI_pct"], 4))
    want = dict(state=XCHECK["state"], order=XCHECK["order"],
                gci_pct=XCHECK["gci_pct"])
    ok = got == want
    if verbose:
        print("-- CROSS-CHECK against a PUBLISHED triple --")
        print("   source: %s" % XCHECK["source"])
        print("   cells %s  values %s  dim %d"
              % (XCHECK["cells"], XCHECK["values"], XCHECK["dim"]))
        print("   published: %s" % want)
        print("   reproduced: %s" % got)
        print("   [%s] the shared instrument reproduces the published row"
              % ("ok " if ok else "BAD"))
        print("   r21 %.4f r32 %.4f (%s form)" % (t["r21"], t["r32"], t["form"]))
    return ok, got, want


# ---------------------------------------------------------------------------
# synthetic trees, on real paths with real mtimes -- no mocking
# ---------------------------------------------------------------------------
_CELLS = {"K2f_L1": 58368, "K2f_L2": 196992, "K2f_L3": 664848}


def _converging_series(target, n=60, start_offset=11.0):
    """A series that converges to `target`, whose last 9 samples span well
    inside 0.02 % of the range it spanned, and whose range is far above 10 ulp
    at the format `materialise_dat` writes."""
    return [target + start_offset * math.exp(-0.45 * i) for i in range(n)]


def _cycling_series(target, n=60, start_offset=11.0, amp_frac=8.0):
    base = _converging_series(target, n, start_offset)
    rng = max(base) - min(base)
    amp = amp_frac * (CYCLE_TOL_PCT / 100.0) * rng
    return [b + amp * math.sin(2 * math.pi * i / 4.0) for i, b in enumerate(base)]


def _mk_series(case, name, values):
    fo = "volFieldValue.dat" if name in ("U_ha", "T_ca") else "surfaceFieldValue.dat"
    d = os.path.join(case, "postProcessing", name, "0")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, fo)
    materialise_dat([CYCLE_INTERVAL * (i + 1) for i in range(len(values))],
                    values, p)
    return p


def _mk_level(root, lv, *, t_in_max, u_ha, t_ca, cells=None, cycling=False,
              geom=3, wedge=0, checkmesh_failed=0, full_flags=True,
              mincell_ok=True, series=True, end_time=3000):
    """A complete synthetic level ON DISK: real files, real mtimes."""
    import time as _t
    cells = cells or _CELLS[lv]
    cd = os.path.join(root, lv)
    os.makedirs(os.path.join(cd, "system"), exist_ok=True)
    os.makedirs(os.path.join(cd, "constant", "polyMesh"), exist_ok=True)
    with open(os.path.join(cd, "system", "controlDict"), "w") as fh:
        fh.write("endTime %d;\ndeltaT 1;\nwriteInterval 500;\n" % end_time)
    with open(os.path.join(cd, "constant", "polyMesh", "owner"), "w") as fh:
        fh.write("FoamFile{}\n// note  \"nPoints: 1 nCells: %d nFaces: 1 \"\n" % cells)
    with open(os.path.join(cd, "constant", "polyMesh", "boundary"), "w") as fh:
        fh.write("6\n(\n" + "walls { type wall; }\n" * 5
                 + ("w { type wedge; }\n" * wedge)
                 + "t { type patch; }\n)\n")
    flags = "checkMesh -allGeometry -allTopology" if full_flags else "checkMesh"
    with open(os.path.join(cd, "log.checkMesh"), "w") as fh:
        fh.write("# COMMAND LINE: %s\n" % flags)
        fh.write("    cells: %d\n" % cells)
        fh.write("Mesh has %d geometric (non-empty/wedge) directions (%s)\n"
                 % (geom, " ".join("1" * max(geom, 1))))
        fh.write("Mesh has 3 solution (non-empty) directions (1 1 1)\n")
        # VERBATIM from a real log.checkMesh -- trailing sentence periods and
        # all.  Scaffolding that emits a tidier artifact than OpenFOAM does is
        # how a reader passes 31 arms and crashes on its first real case.
        fh.write("    Min volume = 0.0004687499981. Max volume = "
                 "0.0006015625022.  Total volume = 28.74.  Cell volumes OK.\n")
        fh.write("Mesh OK.\n" if checkmesh_failed == 0
                 else "***Bad cells\nFailed %d mesh checks\n" % checkmesh_failed)
    mm = {f: (0.02 if mincell_ok else 0.001) for f in NAMED_FEATURES}
    with open(os.path.join(cd, "MINCELL.json"), "w") as fh:
        json.dump(mm, fh)
    # rule 4: 0/T first, then the endTime fields, so the age guard has a referent
    os.makedirs(os.path.join(cd, "0"), exist_ok=True)
    open(os.path.join(cd, "0", "T"), "w").write("0\n")
    _t.sleep(0.02)
    ed = os.path.join(cd, str(end_time))
    os.makedirs(ed, exist_ok=True)
    for f in MD.NEEDED:
        open(os.path.join(ed, f), "w").write("x\n")
    with open(os.path.join(cd, "log.solve"), "w") as fh:
        for i in range(end_time):
            fh.write("ExecutionTime = %.2f s  ClockTime = %d s\n" % (i * 0.1, i))
        fh.write("End\n")
    with open(os.path.join(root, "STATUS.%s" % lv), "w") as fh:
        fh.write("case=%s\nrc=0\nwall_s=100\nranks=4\ncore_min=6.667\n" % lv)
    if series:
        gen = _cycling_series if cycling else _converging_series
        for i in range(N_RACKS):
            # rack 0 is the end rack and is the hottest, so T_in,max == T_in_0
            _mk_series(cd, "T_in_%d" % i, gen(t_in_max - 0.4 * i))
        _mk_series(cd, "U_ha", gen(u_ha, start_offset=0.9))
        _mk_series(cd, "T_ca", gen(t_ca, start_offset=4.0))
    return cd


def _mk_tree(root, *, p_order=2.0, cycling_levels=(), series_levels=LEVELS,
             **kw):
    """A three-level tree whose G1 triple has a KNOWN observed order."""
    r = 1.5 ** p_order            # value ratio between consecutive levels
    fine, med, coarse = 0.1, 0.1 * r, 0.1 * r * r
    base = 300.0
    tgt = {"K2f_L3": base + fine, "K2f_L2": base + med, "K2f_L1": base + coarse}
    for lv in LEVELS:
        _mk_level(root, lv, t_in_max=tgt[lv],
                  u_ha=0.5 + (tgt[lv] - base) * 0.01,
                  t_ca=290.0 + (tgt[lv] - base) * 0.1,
                  cycling=(lv in cycling_levels),
                  series=(lv in series_levels), **kw)
    return root


# ---------------------------------------------------------------------------
# selftest -- the mutation matrix, s.9.6
# ---------------------------------------------------------------------------
def selftest():
    ok_all = True

    def arm(label, got, want):
        nonlocal ok_all
        good = (got == want)
        ok_all = ok_all and good
        print("  [%s] %s" % ("ok " if good else "BAD", label))
        if not good:
            print("        got %r, wanted %r" % (got, want))

    def arm_refuses(label, fn):
        nonlocal ok_all
        try:
            fn()
            ok_all = False
            print("  [BAD] %s -- did NOT refuse" % label)
        except Refuse as e:
            print("  [ok ] %s -- REFUSED: %s" % (label, str(e)[:90]))

    print("-- THE WIRING AUDIT: a freeze verifies BYTES, never that anything "
          "CALLS them --")
    ok, unreachable, reached, collisions = wiring_audit()
    arm("every registered gate function is reachable from main() BY BARE NAME, "
        "and no gate name collides with an attribute (%d of %d)"
        % (len(reached), len(GATE_FUNCTIONS)), ok, True)
    if unreachable:
        print("        UNREACHABLE FROM main(): %s" % ", ".join(unreachable))
    if collisions:
        print("        NAME COLLISION -- a gate name is also used as an "
              "attribute, which the first form of this audit would have read as "
              "REACHABLE without a call: %s" % ", ".join(collisions))
    print("        K2d's four orphans -- read_checkmesh, read_patch_census, "
          "gate_mincell, built_cell_count -- would have failed this arm.")

    print("\n-- the shared instruments reproduce a PUBLISHED row --")
    xok, got, want = cross_check(verbose=True)
    arm("T23G2R Q4: order 0.9917, GCI 2.0576 %, CONVERGING", xok, True)

    print("\n-- rule 5's ORDERING is checked against roache_triple.grade_ladder --")
    # a VALUE-banded ladder, where grade_ladder IS applicable, driven through
    # both paths.  The shared instrument stays the authority on the ordering.
    for label, states, band, want_v in (
            ("CONVERGING inside band", {"c": "CONVERGED", "m": "CONVERGED",
                                        "f": "CONVERGED"}, (0.0, 1.0), "PASS"),
            ("a level not converged -> NOT A RESULT",
             {"c": "CYCLING", "m": "CONVERGED", "f": "CONVERGED"},
             (0.0, 1.0), "NOT A RESULT"),
            ("outside the band -> GATE FAIL",
             {"c": "CONVERGED", "m": "CONVERGED", "f": "CONVERGED"},
             (10.0, 11.0), "GATE FAIL")):
        lv = [dict(name="c", cells=2500, value=0.50625),
              dict(name="m", cells=2500 * 2.25 ** 2, value=0.225),
              dict(name="f", cells=2500 * 2.25 ** 4, value=0.1)]
        row = RT.grade_ladder("probe", lv, 2, band,
                              RT.external_plant_control("probe", 0.0, RT.PLANT),
                              iterative_states=states)
        arm("grade_ladder: %s" % label, row["verdict"], want_v)

    print("\n-- the reader, and the planted-zero control on it --")
    root = tempfile.mkdtemp(prefix="k2f_self_")
    try:
        _mk_tree(root, p_order=2.0)
        cd = os.path.join(root, "K2f_L1")
        p = series_path(cd, "U_ha")
        its, vals, raw = read_dat_series(p)
        arm("the production reader returns the series it was pointed at",
            len(vals) == 60 and len(its) == 60, True)
        pc = planted_zero_control(cd, "U_ha")
        arm("CONTROL: the reader SEES a planted %g" % RT.PLANT, pc["passed"], True)
        arm("...and so does the gate's own path (check_convergence)",
            abs(pc["gate_path_delta"] - RT.PLANT) <= RT.PLANT_READBACK_TOL, True)

        blind = os.path.join(root, "blind.dat")
        materialise_dat([50 * (i + 1) for i in range(12)], [1.0] * 12, blind)
        arm_refuses("NULL VARIATION: a series that never moved -> REFUSE, "
                    "not CONVERGED",
                    lambda: classify_cycle(blind, "blind"))

        # A RESTART WRITES THE SECOND FILE IN A NEW TIME DIRECTORY, not beside
        # the first.  The arm's first form wrote a surfaceFieldValue.dat next to
        # a volFieldValue.dat, which the reader's glob does not span -- the arm
        # did not fire and the reader was never tested.  An arm never shown able
        # to fail is not an arm, and this one was silently in that state.
        restart = os.path.join(cd, "postProcessing", "U_ha", "500")
        os.makedirs(restart, exist_ok=True)
        open(os.path.join(restart, "volFieldValue.dat"), "w").write(
            "# the SECOND file, as a restart writes it\n50 1\n")
        arm_refuses("GLOB COLLISION: a restart's SECOND function-object file "
                    "-> REFUSE, not a wrong number",
                    lambda: series_path(cd, "U_ha"))
        shutil.rmtree(restart)

        ragged = os.path.join(root, "ragged.dat")
        open(ragged, "w").write("# t v\n50 1.0 2.0\n100 1.1 2.1\n")
        arm_refuses("a three-column series -> REFUSE rather than read partially",
                    lambda: read_dat_series(ragged))
        empty = os.path.join(root, "empty.dat")
        open(empty, "w").write("# header only\n")
        arm_refuses("an EMPTY series file -> REFUSE (A-INPUT, s.3.1)",
                    lambda: read_dat_series(empty))

        print("\n-- G-CYCLE, and the detector shown able to detect a cycle --")
        conv = classify_cycle(series_path(cd, "U_ha"), "L1::U_ha")
        arm("a converging series reads CONVERGED", conv["state"], "CONVERGED")
        arm("...through the SHARED classifier, not a local copy",
            conv["shared_instrument"], "check_convergence.classify_monitor")
        arm("...on the range-spanned normaliser (D389)",
            "range spanned" in conv["normaliser"], True)
        tmpd = tempfile.mkdtemp(prefix="k2f_cyc_")
        cyc = classify_series_values(_cycling_series(300.1), "probe", tmpd)
        arm("a planted limit cycle reads CYCLING", cyc["state"], "CYCLING")
        drift = classify_series_values(
            [300.0 + 2.0 * (1 - i / 60.0) for i in range(60)], "drift", tmpd)
        arm("a monotone drift reads DRIFTING, not CYCLING", drift["state"],
            "DRIFTING")
        pcc = planted_cycle_control(read_dat_series(series_path(cd, "U_ha"))[1],
                                    "L1::U_ha", tmpd)
        arm("planted-cycle positive arm fires", pcc["positive_arm"], "CYCLING")
        arm("planted-cycle negative arm does NOT fire",
            pcc["negative_arm"] != "CYCLING", True)
        arm("a MEASURED detection floor is reported beside CONVERGED",
            pcc["detection_floor_frac_of_threshold"] is not None, True)
        shutil.rmtree(tmpd, ignore_errors=True)

        print("\n-- mesh gates --")
        cm = read_checkmesh(cd)
        arm("CONTROL: the registered build passes G-CHECKMESH",
            gate_checkmesh(cm)[0], True)
        arm("THE TRAILING-PERIOD TRAP: `Min volume = 0.0004687499981.` parses "
            "(analyse_k2d.py:193's regex raises ValueError here)",
            abs(cm["min_volume"] - 0.0004687499981) < 1e-15, True)
        arm("CONTROL: G-3D confirms three GEOMETRIC directions",
            gate_3d(cm, read_patch_census(cd))[0], True)
        arm("CONTROL: G-MINCELL passes above the floor", gate_mincell(cd)[0], True)
        arm("CONTROL: the BUILT count is read from polyMesh, not a target",
            built_cell_count(cd), _CELLS["K2f_L1"])
        arm("CONTROL: G-MESHSIM passes on the registered ladder",
            gate_meshsim(_CELLS)[0], True)
        arm("MUTATION: a step outside [3.2063, 3.5438] -> FAIL",
            gate_meshsim({"K2f_L1": 58368, "K2f_L2": 100000,
                          "K2f_L3": 664848})[0], False)
        arm("MUTATION: a log WITHOUT the two flags -> REFUSED by provenance",
            gate_checkmesh(dict(path="x", provenance_full_set=False,
                                n_failed=0, failed_lines=[]))[0], False)
        arm("MUTATION: `Mesh OK.` is NOT accepted without the flags",
            gate_checkmesh(dict(path="x", provenance_full_set=False, n_failed=0,
                                failed_lines=[]))[0], False)
        arm("MUTATION: no verdict line at all -> UNMEASURED IS NOT PASSING",
            gate_checkmesh(dict(path="x", provenance_full_set=True,
                                n_failed=None, failed_lines=[]))[0], False)
        arm("MUTATION: a failed mesh check with an EMPTY tolerance registry -> FAIL",
            gate_checkmesh(dict(path="x", provenance_full_set=True, n_failed=2,
                                failed_lines=["***Bad"]))[0], False)
        arm("MUTATION: THE WEDGE TRAP -- 2 geometric, 3 solution -> REFUSED",
            gate_3d(dict(path="x", n_geometric=2, geometric_line="g"),
                    {"empty": 0, "wedge": 2})[0], False)
        arm("MUTATION: 3 geometric but a wedge patch present -> REFUSED",
            gate_3d(dict(path="x", n_geometric=3, geometric_line="g"),
                    {"empty": 0, "wedge": 2})[0], False)
        arm("MUTATION: no geometric line at all -> REFUSED",
            gate_3d(dict(path="x", n_geometric=None, geometric_line=None),
                    {"empty": 0, "wedge": 0})[0], False)
        bad = _mk_level(root, "K2f_L1", t_in_max=300.1, u_ha=0.5, t_ca=290.0,
                        mincell_ok=False)
        arm("MUTATION: a SUB-FLOOR minimum cell is caught",
            gate_mincell(bad)[0], False)

        print("\n-- G-STATEINV (s.0.3) --")
        arm("CONTROL: one state across the ladder is admissible",
            gate_stateinv({"U_ha": {lv: "CONVERGED" for lv in LEVELS}})[0], True)
        arm("MUTATION: a CONVERGED/CYCLING split is INVALID IN PRINCIPLE",
            gate_stateinv({"U_ha": {"K2f_L1": "CONVERGED",
                                    "K2f_L2": "CYCLING",
                                    "K2f_L3": "CYCLING"}})[0], False)

        print("\n-- the one-way gate --")
        try:
            _seal_oneway(dict(row="X", verdict="PASS"), "GATE FAIL")
            arm("ONE-WAY: GATE FAIL rehabilitated to PASS is refused", False, True)
        except RuntimeError:
            arm("ONE-WAY: GATE FAIL rehabilitated to PASS is refused", True, True)
        try:
            _seal_oneway(dict(row="X", verdict="roughly converged"), None)
            arm("VOCABULARY: a synonym is refused", False, True)
        except RuntimeError:
            arm("VOCABULARY: a synonym is refused", True, True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\n-- A-DRIVE (s.7): main() POINTED AT A DIRECTORY, both directions --")
    root = tempfile.mkdtemp(prefix="k2f_drive_")
    try:
        _mk_tree(root, p_order=2.0)
        code, rep = grade(root)
        arm("direction 1: a complete tree returns a VERDICT SET, not a stub",
            (code == EXIT_OK and len(rep["verdicts"]) == 4), True)
        arm("...and every verdict is in the fixed vocabulary",
            all(v in RT.VERDICTS for v in rep["verdicts"].values()), True)
        arm("...G1 reads PASS at a planted observed order of 2.0",
            rep["verdicts"].get("G1"), "PASS")
        arm("...and its observed order reproduces the plant",
            round(rep["rows"][0]["order"], 4), 2.0)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = tempfile.mkdtemp(prefix="k2f_drive2_")
    try:
        _mk_tree(root, p_order=2.0, series_levels=("K2f_L1", "K2f_L2"))
        code, rep = grade(root)
        arm("direction 2: a level with NO SERIES -> NAMED refusal at exit 2",
            code, EXIT_REFUSE)
        arm("...naming the missing input, not 'nothing to grade'",
            bool(rep["refusals"]) and "postProcessing" in rep["refusals"][0], True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = tempfile.mkdtemp(prefix="k2f_drive3_")
    try:
        _mk_tree(root, p_order=2.0, cycling_levels=("K2f_L2", "K2f_L3"))
        code, rep = grade(root)
        arm("direction 3: a CONVERGED/CYCLING ladder -> every row NOT A RESULT",
            set(rep["verdicts"].values()), {"NOT A RESULT"})
        arm("...and S-ONSET is reported beside it",
            len(rep["s_onset"]["rows"]) == 6, True)
        arm("...with decomp_control labelled NOT RUN (s.18.3)",
            rep["s_onset"]["decomp_control"], "NOT RUN")
        arm("...and G-STATEINV names the s.0.3 mechanism independently",
            "INVALID IN PRINCIPLE" in rep["stateinv"]["why"], True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = tempfile.mkdtemp(prefix="k2f_drive4_")
    try:
        _mk_tree(root, p_order=2.0)
        shutil.rmtree(os.path.join(root, "K2f_L3"))
        code, rep = grade(root)
        arm("direction 4: a MISSING LEVEL -> NAMED refusal naming the level",
            code == EXIT_REFUSE and "K2f_L3" in rep["refusals"][0], True)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\nSELFTEST %s" % ("PASS -- every arm fired as registered" if ok_all
                             else "FAIL -- an arm did not behave as registered"))
    return EXIT_OK if ok_all else EXIT_FAIL


def main(argv):
    """Take a case directory and return a verdict.  s.7, `A-DRIVE`.

    THE ENTRY POINT K2d DID NOT HAVE.  `analyse_k2d.py:613-619` was a two-branch
    stub -- `--selftest`, or a hardcoded refusal -- and that is the whole reason
    this rung exists.
    """
    if argv and argv[0] == "--selftest":
        return selftest()
    if argv and argv[0] == "--xcheck":
        ok, _got, _want = cross_check()
        return EXIT_OK if ok else EXIT_FAIL
    root = argv[0] if argv else HERE
    out = argv[1] if len(argv) > 1 else None
    if not os.path.isdir(root):
        print("REFUSED (exit 2): %s is not a directory. This comparator grades a "
              "CASE ROOT holding %s." % (root, ", ".join(LEVELS)))
        return EXIT_REFUSE
    code, report = grade(root, out_json=out)
    print_report(report, code)
    return code


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e)
        sys.exit(EXIT_REFUSE)
