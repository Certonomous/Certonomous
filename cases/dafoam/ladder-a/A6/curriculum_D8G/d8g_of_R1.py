#!/usr/bin/env python
"""Curriculum D8G PRODUCER -- A6 CRM wing-alone, THREE-LEVEL GRID-CONVERGENCE TRIPLE at
r = 2 on TWO TOOLCHAIN ROWS.  THREE MODES: P (one cold primal at a level), A (the L2
adjoint `compute_totals` at the baseline design), F (the L2 central-FD table beside it,
INCLUDING the section-4 trivial-baseline step).  NO OPTIMISER RUNS IN THIS ITEM.

PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.  The freeze is the
dafoam-supervisor's act (CLAUDE.md rule 2) and this file's md5 is recorded in the
launcher's INSTRUMENT_MD5S manifest and in PREREGISTRATION.md at that commit.

THE DIRECTION OF FIT, WHICH IS THE WHOLE POINT: `d8g_grade.py` IS THE SPECIFICATION AND
THIS FILE CONFORMS TO IT.  Nothing here may be satisfied by editing the comparator.  Every
key written below is a key the comparator's read_P / read_A / read_F / ctrl_control /
grader_plant_control actually reads, and `d8g_of_selftest.sh` drives producer-built
artefacts THROUGH THE COMPARATOR'S OWN READERS to prove it -- because a key the grader
reads and the producer never writes is a rung that dies at grading time, after the compute
is spent.

DERIVED FROM cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_of.py -- a FROZEN instrument
behind a graded two-row PASS, WHICH THIS FILE DOES NOT EDIT.  The deltas are recorded in
d8g_of_DELTAS_from_d8r.diff.  INHERITED UNCHANGED IN SHAPE: the frozen-producer md5
refusal and header exec, the rank-0 file rule, the emit/fsync discipline, idwarp_identity,
the central-difference table, and the CTRL planted-zero control row.  REMOVED because D8G
runs no optimiser: mode O, IPOPT_OPTS, TRIM, read_ipopt_terminus, the endpoint file.  NEW
here: mode P and mode A, the level argument, the MEASURED cell count with its independent
cross-check, the controlDict/daOptions read-back with the PLATEAU-WINDOW FORECAST that
refuses BEFORE compute is spent, the trivial-baseline step, the same-row gradient
provenance check, the mesh-immutability and age-datum-immutability checks, the
CTRL-collision guard and the WRITTEN-ARTEFACT READ-BACK.

THIS FILE RENDERS NO VERDICTS.  It writes artefacts and refuses; the comparator judges.
No `assert` anywhere (L-332).  No unconditional success print: each terminal marker is
printed only after its artefact is written, fsynced AND read back.

L-342.  PHYSICS fields (the mesh, the cell count, the acceptance pair, endTime, CD/CL, the
staged gradient in mode F) absent or unparseable -> REFUSE, exit 2.  INFRASTRUCTURE fields
(the in-process libidwarp.so md5, wall times, the owner-body cross-check on a non-ascii
mesh) absent -> recorded as NOT_MEASURED and DISCLOSED in the artefact's `not_measured`
list, never silently filled and never composed into anything.

THE ARTEFACT CONTRACT THIS FILE WRITES -- read from d8g_grade.py's read_P / read_A /
read_F / ctrl_control / grader_plant_control, not from prose:
  d8g_P.json  {item, mode:"P", level, cells:int, nprocs:int, identity:{libidwarp_so_md5},
               points_md5, endTime, CD, CL}
  d8g_A.json  {item, mode:"A", level, nprocs:int, identity, points_md5,
               CD_baseline, CL_baseline,
               adjoint:{CD:{twist:[...],patchV:[...]}, CL:{twist:[...],patchV:[...]}}}
  d8g_F.json  {item, mode:"F", level, nprocs:int, identity, components_requested, steps,
               trivial_step, adjoint_source:{md5}, CD_baseline, CL_baseline, eta_used,
               rows:[{dv,idx,status,fd:{repr(step):{step,ok,dCD,dCL}}}, ...,
                     {dv:"CTRL",idx:0,status:"CONTROL",fd:{...},planted:{...}}]}
TYPES THAT ARE LOAD-BEARING, because the comparator compares them by identity and not by
value: `cells` and `nprocs` are INTEGERS (read_P/grade() use `!=` against the registered
ints, so a string would REFUSE); `components_requested` is a LIST OF [str,int] LISTS equal
to COMPONENTS_REGISTERED or read_F refuses; `trivial_step` is 1.0e-3 to within 1e-15 or
read_F refuses; the CTRL row's `fd` key is literally `repr(CTRL_STEP)` == "0.1" because
ctrl_control indexes the RAW row by that string.  Physical measurements are written as
`repr(float)` strings (D8R's convention) -- the comparator applies float() to every one.

THE PLATEAU WINDOW IS FORECAST AND REFUSED BEFORE COMPUTE.  G-PLAT reads the solver's own
`CD:`/`CL:` lines at printInterval and makes a level NOT A RESULT FOR WANT OF EVIDENCE if
the window holds fewer than 10 samples.  MEASURED first-hand on the D8R producer's own arm
/home/ubuntu/certonomous-runs/CURRICULUM-D8R-a6-twist-opt-conv/F-P_20260827T235119Z_1656338.log:
32 `Running Primal Solver` calls, 3,232 `CD:` lines, and the LAST primal segment carries
EXACTLY 101 `CD:` samples at `Time = 1, 10, 20, ... 1000` -- controlDict `endTime 1000`,
`deltaT 1`, daOptions `printInterval 10`.  n = |{1} u {10,20,...,1000}| = 101; window =
min(max(ceil(0.10 x 101), 10), 101) = 11 >= 10.  This file RECOMPUTES that arithmetic from
the arm's OWN controlDict and daOptions at startup and EXITS 2 BEFORE the solver runs if
the forecast window is below 10.  A level that cannot be judged is not worth its core-min.

WHAT THIS FILE MUST NEVER DO, and is unit-tested not to: emit any line that the
comparator's log readers would parse as the SOLVER'S OWN output.  A producer that echoed
`    primalMinResTol 1e-08;` would be forging the exact evidence G-PRIMAL reads back.
Every line this file prints is prefixed `D8G_` and is checked against the comparator's four
log regexes in the selftest.
"""
import gzip
import hashlib
import json
import math
import os
import re
import sys
import time

# ---- REGISTERED CONSTANTS (PREREGISTRATION.md; the document governs) ------------------
ITEM = "D8G"
SCENARIO = "scenario1"
PRODUCER = "d8g_runScript.py"
# PINNED, 2026-09-11.  THE PRODUCER SCRIPT NOW EXISTS AND THIS IS NOT A GUESS: it is a
# BYTE COPY of curriculum_D8R/d8r_runScript.py, which is itself a byte copy of D8's frozen
# opt/runScript.py -- ALL THREE HASH TO THE VALUE BELOW, verified against all three paths.
# PREREGISTRATION.md:316 registers the identity in as many words ("because D8G's producer
# is D8R's"), so pinning this constant records a registered fact rather than choosing one.
# d8g_runScript_contract.py's U1-U4 re-prove the identity and refuse the archived A6
# tutorial runScript (0de915d21166a91a9a54b37ab11214cf), the WRONG file that sits in the
# same staging tree carrying a different acceptance pair.
PRODUCER_MD5 = "28c7819487a025a5f6554d38062a2b66"
ANCHOR = "# OpenMDAO setup"

LEVELS = ("L1", "L2", "L3")
FD_LEVEL = "L2"                                   # section 4.7
CELLS_REGISTERED = {"L1": 5568, "L2": 44544, "L3": 356352}      # section 2.2

DVS = ("twist", "patchV")
# The REGISTERED SUBSET, named in advance (D8 RESULTS.md T2), inherited from D8R.
# twist[2] is not in the subset; twist[6] is NOT A RESULT BY NAME (D8 section 6) and is
# NOT TOUCHED -- it is never perturbed, never differenced and never aggregated.
COMPONENTS = [("twist", 0), ("twist", 1), ("twist", 3), ("twist", 4), ("twist", 5)]
UNTOUCHED_BY_NAME = {"twist[6]": "NOT A RESULT BY NAME, D8 section 6 -- never perturbed",
                     "twist[2]": "outside the registered subset -- never perturbed"}
STEPS = {"twist": [3.0e-2, 1.0e-1, 3.0e-1]}       # degrees; the MIDDLE is the reference
TRIVIAL_STEP = 1.0e-3                             # section 4 trivial baseline, PREDICTED > 15 %
CTRL_STEP = 1.0e-1
CTRL_NAME = "CTRL"
PLANT = 1.234e-03                                 # standing rule 3
ETA_FLOOR = 1.0e-14

# ---- the acceptance pair G-PRIMAL reads BACK OUT OF THE LOG (section 4.5) -------------
REGISTERED_DAOPTIONS = {"solverName": "DARhoSimpleCFoam",
                        "primalMinResTol": 1.0e-8,
                        "primalMinResTolDiff": 1.0e4,
                        "primalMinIters": 1000,
                        "printInterval": 10}
REGISTERED_CONTROLDICT = {"endTime": 2000.0, "deltaT": 1.0, "stopAt": "endTime"}  # D8G-R1 REPAIR ADDENDUM 7: R3 package knob 5 (endTime 2000). ONLY delta from the frozen d8g_of.py f17b4a26fc5dcbbb44e9c820ba16df6c.
PLATEAU_WINDOW_FRAC = 0.10                        # mirrors d8g_grade.PLAT_WINDOW_FRAC
PLATEAU_MIN_SAMPLES = 10                          # mirrors d8g_grade.PLAT_MIN_SAMPLES

OUT = {"P": "d8g_P.json", "A": "d8g_A.json", "F": "d8g_F.json"}
JSONL = {"P": "d8g_P.jsonl", "A": "d8g_A.jsonl", "F": "d8g_F.jsonl"}
TERMINAL = {"P": "D8G_P_WRITTEN", "A": "D8G_A_WRITTEN", "F": "D8G_F_WRITTEN"}
GRADIENT_IN = "d8g_A_gradient.json"               # d8g_run_arm.sh copies the SAME ROW's d8g_A.json here
AGE_DATUM_FILE = ".d8g_age_datum"
AGE_DATUM_REF = os.path.join("0", "U")            # d8g_grade.DATUM_REF
POLYMESH = os.path.join("constant", "polyMesh")
POINTS = os.path.join(POLYMESH, "points.gz")
CONTROLDICT = os.path.join("system", "controlDict")

NOT_MEASURED = "NOT_MEASURED"
EXPECTED_UNITS = 54                               # the selftest's frozen unit count


class Refusal(Exception):
    """A refusal is not a verdict.  This instrument renders no verdicts."""


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


# ================= small readers ======================================================
def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def _read_text_maybe_gz(path):
    """A polyMesh file is `<name>` or `<name>.gz`; both are read the same way."""
    if path.endswith(".gz"):
        with gzip.open(path, "rt", errors="replace") as fh:
            return fh.read()
    with open(path, errors="replace") as fh:
        return fh.read()


def polymesh_file(polymesh_dir, name):
    """Returns the existing spelling of a polyMesh member, or None."""
    for cand in (os.path.join(polymesh_dir, name + ".gz"), os.path.join(polymesh_dir, name)):
        if os.path.isfile(cand):
            return cand
    return None


_RE_NOTE_NCELLS = re.compile(r"note\s+\"[^\"]*nCells:\s*(\d+)")
_RE_FOAM_FORMAT = re.compile(r"^\s*format\s+(\w+)\s*;", re.M)


def read_cells_from_note(owner_path):
    """READER 1 -- the mesh writer's own header note on `owner`:
    note "nPoints:45104  nCells:41760  nFaces:128574  nInternalFaces:121986";
    MEASURED shape, first-hand, on the D8R graded arm's constant/polyMesh/owner.gz."""
    head = _read_text_maybe_gz(owner_path)[:4096]
    m = _RE_NOTE_NCELLS.search(head)
    if m is None:
        return None
    return int(m.group(1))


def read_cells_from_owner_body(owner_path):
    """READER 2 -- INDEPENDENT OF READER 1.  nCells == max(owner) + 1, computed from the
    face-owner list itself, so a stale or hand-edited header note cannot agree with it by
    construction.  Returns None (NOT_MEASURED, disclosed) when the mesh is not written in
    `format ascii` -- the cross-check is then unavailable and says so rather than
    returning a number it did not measure."""
    txt = _read_text_maybe_gz(owner_path)
    fm = _RE_FOAM_FORMAT.search(txt[:4096])
    if fm is None or fm.group(1) != "ascii":
        return None
    m = re.search(r"\n\s*(\d+)\s*\n\(\n", txt)
    if m is None:
        return None
    start = m.end()
    end = txt.find("\n)", start)
    if end < 0:
        return None
    body = txt[start:end].split()
    if not body:
        return None
    try:
        return max(int(v) for v in body) + 1
    except ValueError:
        return None


def measure_cells(polymesh_dir):
    """THE CELL COUNT IS MEASURED FROM THE MESH, NEVER TAKEN FROM THE LEVEL NAME.  Taking
    it from the level would make the comparator's `cells == CELLS[level]` check
    self-fulfilling: the artefact would say 5,568 because it was told the arm is L1, not
    because the mesh has 5,568 cells.  Two independent readers; a disagreement REFUSES."""
    owner = polymesh_file(polymesh_dir, "owner")
    if owner is None:
        refuse("CELLS", {"owner_absent_in": polymesh_dir,
                         "note": "the mesh is the case; a PHYSICS field absent -> REFUSE (L-342)"})
    note = read_cells_from_note(owner)
    if note is None:
        refuse("CELLS", {"owner_header_note_absent_or_unparseable": owner,
                         "note": "the cell count is a PHYSICS field; present-but-garbage -> REFUSE"})
    body = read_cells_from_owner_body(owner)
    out = {"cells": int(note), "cells_from_owner_header_note": int(note),
           "cells_from_owner_body_max_plus_1": (int(body) if body is not None else NOT_MEASURED),
           "owner_file": owner, "readers_agree": (body == note) if body is not None else NOT_MEASURED}
    if body is not None and int(body) != int(note):
        refuse("CELLS", {"independent_cell_readers_disagree": {"header_note": int(note),
                                                               "owner_body_max_plus_1": int(body),
                                                               "file": owner},
                         "note": "a header note that disagrees with the mesh it describes is "
                                 "present-but-garbage -> REFUSE (L-342)"})
    return out


_RE_CD_KEY = {"endTime": re.compile(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", re.M),
              "deltaT": re.compile(r"^\s*deltaT\s+([0-9.eE+-]+)\s*;", re.M),
              "writeInterval": re.compile(r"^\s*writeInterval\s+([0-9.eE+-]+)\s*;", re.M)}
_RE_CD_STOPAT = re.compile(r"^\s*stopAt\s+(\w+)\s*;", re.M)


def read_controldict(path):
    """endTime / deltaT / stopAt, read from the arm's OWN system/controlDict.  endTime is a
    PHYSICS field -- rule 4's completion clause is `last time == endTime`."""
    if not os.path.isfile(path):
        refuse("CONTROLDICT", {"absent": path, "note": "endTime is a PHYSICS field -> REFUSE"})
    txt = open(path, errors="replace").read()
    out = {}
    for k, rex in _RE_CD_KEY.items():
        m = rex.search(txt)
        out[k] = (float(m.group(1)) if m else None)
    m = _RE_CD_STOPAT.search(txt)
    out["stopAt"] = (m.group(1) if m else None)
    for k in ("endTime", "deltaT"):
        if out[k] is None:
            refuse("CONTROLDICT", {"key_absent": k, "file": path,
                                   "note": "a PHYSICS field absent -> REFUSE (L-342)"})
    return out


def check_registered_controldict(cd):
    """Returns the list of departures from the registered controlDict.  EMPTY IS THE ONLY
    ACCEPTABLE ANSWER: a family whose time control changes between levels is not a family."""
    bad = []
    for k in ("endTime", "deltaT"):
        if cd.get(k) is None or abs(float(cd[k]) - REGISTERED_CONTROLDICT[k]) > 1e-12:
            bad.append({"key": k, "got": cd.get(k), "registered": REGISTERED_CONTROLDICT[k]})
    if cd.get("stopAt") != REGISTERED_CONTROLDICT["stopAt"]:
        bad.append({"key": "stopAt", "got": cd.get("stopAt"), "registered": REGISTERED_CONTROLDICT["stopAt"]})
    return bad


def daoptions_report_line(daOptions):
    """THE PAIR IS REPORTED IN THIS INSTRUMENT'S OWN SYNTAX AND NEVER THE SOLVER'S.  G-PRIMAL
    must read `primalMinResTol` / `primalMinResTolDiff` back out of DAFoam's OWN daOption
    dump; a producer line that parsed as that dump would be FORGED EVIDENCE for the exact
    gate the comparator refuses on.  This is the line main() prints, and the selftest checks
    THIS function's output against the comparator's own log regexes -- not a copy of it."""
    return ("DAOPTIONS_CHECK_OK solverName=%s primalMinResTol_value=%r primalMinResTolDiff_value=%r "
            "printInterval_value=%r primalMinIters_value=%r "
            "(reported in D8G syntax; the comparator reads the SOLVER'S dump, never this line)"
            % (daOptions.get("solverName"), daOptions.get("primalMinResTol"),
               daOptions.get("primalMinResTolDiff"), daOptions.get("printInterval"),
               daOptions.get("primalMinIters")))


def check_registered_daoptions(daOptions):
    """G-PRIMAL reads `primalMinResTol` and `primalMinResTolDiff` BACK OUT OF THE ARM'S OWN
    LOG and a mismatch is a GRADER REFUSAL, not a soft note -- and A6 itself carries TWO
    different primalMinResTolDiff values (10000 in the D8R producer, 100 in the archived
    tutorial).  So this instrument checks the pair HERE, before any compute, and refuses
    rather than spending an arm that will be refused at grading time.
    THIS FUNCTION NEVER PRINTS THE PAIR IN THE SOLVER'S OWN SYNTAX -- see the module
    docstring: echoing `    primalMinResTol 1e-08;` would forge the evidence G-PRIMAL
    reads back."""
    bad = []
    for k, want in REGISTERED_DAOPTIONS.items():
        got = daOptions.get(k)
        if isinstance(want, str):
            if got != want:
                bad.append({"key": k, "got": got, "registered": want})
        elif got is None:
            bad.append({"key": k, "got": None, "registered": want})
        else:
            try:
                ok = abs(float(got) - float(want)) <= 1e-12 * max(1.0, abs(float(want)))
            except (TypeError, ValueError):
                ok = False
            if not ok:
                bad.append({"key": k, "got": got, "registered": want})
    return bad


# ================= THE PLATEAU-WINDOW FORECAST (refused BEFORE compute) ================
def printed_sample_count(end_time, delta_t, print_interval):
    """The number of printed `CD:` samples one primal will emit.  DAFoam prints the block
    when `iter % printInterval == 0` OR `iter == 1`, so the count is the size of the SET
    {1} u {printInterval, 2*printInterval, ... <= N}, N = endTime/deltaT.  MEASURED
    first-hand against the D8R arm: endTime 1000, deltaT 1, printInterval 10 -> 101, and
    the log's last primal segment carries exactly 101 `CD:` lines at Time = 1, 10, ...,
    1000.  Computed as a set so the printInterval == 1 double-count cannot creep in."""
    if delta_t <= 0 or print_interval <= 0 or end_time <= 0:
        return 0
    n_iter = int(round(float(end_time) / float(delta_t)))
    pi = int(round(float(print_interval)))
    printed = {1} if n_iter >= 1 else set()
    printed.update(range(pi, n_iter + 1, pi))
    return len(printed)


def plateau_window_size(n):
    """MIRRORS d8g_grade.plateau_window() EXACTLY: the last 10 % of printed samples OR the
    last 10 samples, whichever is LARGER, capped at n."""
    if n <= 0:
        return 0
    return min(max(int(math.ceil(PLATEAU_WINDOW_FRAC * n)), PLATEAU_MIN_SAMPLES), n)


def forecast_plateau_window(end_time, delta_t, print_interval):
    n = printed_sample_count(end_time, delta_t, print_interval)
    w = plateau_window_size(n)
    return {"endTime": end_time, "deltaT": delta_t, "printInterval": print_interval,
            "n_printed_samples_expected": n, "plateau_window_expected": w,
            "floor": PLATEAU_MIN_SAMPLES, "sufficient": bool(w >= PLATEAU_MIN_SAMPLES),
            "arithmetic": "n = |{1} u {pi, 2pi, ... <= endTime/deltaT}| ; window = "
                          "min(max(ceil(0.10 n), 10), n) ; G-PLAT makes the level NOT A RESULT "
                          "FOR WANT OF EVIDENCE below the floor"}


# ================= identity ===========================================================
def idwarp_identity():
    """The in-process libidwarp.so md5 -- THE HASH IS THE IDENTITY, NEVER THE VERSION
    STRING (DAFOAM_CHARTER.md section 11).  An import failure is INFRASTRUCTURE: it is
    recorded as NOT_MEASURED and disclosed; this instrument does not decide what that
    means, G9 does."""
    try:
        import idwarp
        p = idwarp.__file__
        so = os.path.join(os.path.dirname(p), "libidwarp.so")
        return {"idwarp_file": p, "libidwarp_so_md5": md5_of(so)}
    except Exception as exc:                                  # noqa: BLE001
        return {"idwarp_file": None, "libidwarp_so_md5": None, "error": repr(exc)[:200]}


def parse_args(argv):
    """`-mode P|A|F  -level L1|L2|L3`, the shape d8g_run_arm.sh invokes."""
    mode = level = None
    for i, a in enumerate(argv):
        if a == "-mode" and i + 1 < len(argv):
            mode = argv[i + 1]
        if a == "-level" and i + 1 < len(argv):
            level = argv[i + 1]
    if mode not in ("P", "A", "F") or level not in LEVELS:
        return None, None
    if mode in ("A", "F") and level != FD_LEVEL:
        return None, None
    return mode, level


def check_producer_md5(path, registered):
    """Fail-closed while the md5 is the unfrozen token.  Returns (ok, got, why)."""
    if not os.path.isfile(path):
        return False, None, "producer %s absent" % path
    got = md5_of(path)
    if got != registered:
        return False, got, "producer md5 %s != frozen %s" % (got, registered)
    return True, got, None


# ================= record builders (pure; the selftest drives these directly) ==========
def _num(x):
    """Physical measurements go out as repr(float) strings -- D8R's convention, and the
    comparator applies float() to every one.  17 significant digits, exact round-trip."""
    return repr(float(x))


def build_P_record(level, cells_rec, nprocs, ident, points_md5, controldict, cd, cl, extra):
    end_time = float(controldict["endTime"])
    return {"item": ITEM, "mode": "P", "level": level,
            "cells": int(cells_rec["cells"]),                   # INT: read_P compares with !=
            "nprocs": int(nprocs),                              # INT: grade() compares with !=
            "identity": ident, "points_md5": points_md5,
            "endTime": (int(end_time) if float(end_time).is_integer() else end_time),
            "CD": _num(cd), "CL": _num(cl),
            "cells_provenance": cells_rec, "controlDict": controldict, **extra}


def build_A_record(level, nprocs, ident, points_md5, cd, cl, jadj, extra):
    return {"item": ITEM, "mode": "A", "level": level, "nprocs": int(nprocs),
            "identity": ident, "points_md5": points_md5,
            "CD_baseline": _num(cd), "CL_baseline": _num(cl),
            "adjoint": jadj, **extra}


def fd_step_set():
    """THE STEPS THE F ARM ACTUALLY EVALUATES: the three registered graded steps PLUS the
    section-4 TRIVIAL BASELINE.  ONE definition, used by main() and by the selftest, so a
    suite cannot pass against a step set the arm would not have run.  The trivial step's
    job is to FAIL: if the deliberately wrong 1e-3 deg step also passes, the comparator
    WITHDRAWS the FD verdict (G-FD-TRIVIAL), and a table that never evaluated it makes the
    comparator's _trivial_baseline REFUSE outright."""
    return sorted(set(STEPS["twist"]) | {TRIVIAL_STEP})


def fd_row(probe, dv, idx, steps, emit=None):
    """A central-difference row.  `probe(dv, idx, delta) -> (CD, CL)` is INJECTED so the
    selftest can drive this exact code with an analytic function and no solver.  Every
    step gets a row -- INCLUDING the ones that fail, which carry ok: False and the error,
    because the comparator's sweep table prints every step including the failed ones."""
    fd = {}
    graded = set(steps) - {TRIVIAL_STEP}
    for s in steps:
        key = repr(s)
        role = "GRADED" if s in graded else "TRIVIAL_BASELINE_CONTROL"
        try:
            cdp, clp = probe(dv, idx, +s)
            cdm, clm = probe(dv, idx, -s)
            fd[key] = {"step": s, "ok": True, "role": role,
                       "dCD": _num((cdp - cdm) / (2.0 * s)), "dCL": _num((clp - clm) / (2.0 * s)),
                       "CD_plus": _num(cdp), "CD_minus": _num(cdm),
                       "CL_plus": _num(clp), "CL_minus": _num(clm)}
        except Exception as exc:                              # noqa: BLE001
            fd[key] = {"step": s, "ok": False, "role": role, "error": repr(exc)[:400]}
        if emit is not None:
            emit({"kind": "fd_step", "dv": dv, "idx": idx, "step": s, "row": fd[key]})
    return {"dv": dv, "idx": idx, "status": "MEASURED", "fd": fd}


def build_ctrl_row(cd0, cl0):
    """THE HARNESS-INJECTED KNOWN CONSTANT (standing rule 3; comparator section 4.8 (iii)).

    WHY A REAL DERIVATIVE CANNOT BE MISTAKEN FOR IT -- four independent reasons, and the
    first two are STRUCTURAL, not numerical:
      1. NAMESPACE.  Its `dv` is "CTRL", which is not a member of DVS and appears in no
         entry of COMPONENTS.  The comparator's read_F pops this row OUT of `rows` into a
         separate `ctrl` slot before it builds `table`, so it can never enter a plateau,
         an aggregate, a sweep row or the trivial baseline -- and the comparator's
         grader_plant_control explicitly skips it.
      2. STATUS.  "CONTROL", never "MEASURED"; and the row carries `synthetic: true` and
         the arithmetic that produced it.
      3. VALUE, ZERO ARM.  Both sides of the difference are the SAME unperturbed design,
         so the numerator is a number minus itself and the derivative is EXACTLY 0.0 --
         not approximately.  A real central difference on a real perturbed pair is exactly
         0.0 with probability ~0 in floating point, and check_ctrl_not_confusable() below
         REFUSES if any measured row ever lands on it.
      4. VALUE, PLANTED ARM.  CD_plus = CD_baseline + PLANT and CD_minus = CD_baseline, so
         the derivative is PLANT / (2 x CTRL_STEP) = 6.17e-3 EXACTLY AND INDEPENDENTLY OF
         CD_baseline.  An instrument that failed to read its own CD would not land on it,
         and the comparator recovers it to 1e-9 relative.
    The plant is on CD ONLY and says so; the CL arm of both halves is the unperturbed
    baseline, so nothing about CL is claimed by this row."""
    zero = 0.0
    planted = PLANT / (2.0 * CTRL_STEP)
    return {"dv": CTRL_NAME, "idx": 0, "status": "CONTROL", "synthetic": True,
            "planted_on": "CD",
            "fd": {repr(CTRL_STEP): {                       # the key is repr(0.1): ctrl_control indexes the RAW row
                "step": CTRL_STEP, "ok": True, "synthetic": True,
                "dCD": _num(zero), "dCL": _num(zero),
                "CD_plus": _num(cd0), "CD_minus": _num(cd0),
                "CL_plus": _num(cl0), "CL_minus": _num(cl0),
                "note": "SYNTHETIC: identical, unperturbed DVs on both sides -> the numerator is a "
                        "number minus itself -> the derivative is EXACTLY 0.0.  No solver call is "
                        "made for this row and none is claimed."}},
            "planted": {"step": CTRL_STEP, "plant": PLANT, "ok": True, "synthetic": True,
                        "dCD": _num(planted), "dCL": _num(zero),
                        "CD_plus": _num(cd0 + PLANT), "CD_minus": _num(cd0),
                        "CL_plus": _num(cl0), "CL_minus": _num(cl0),
                        "note": "SYNTHETIC: CD_plus = CD_baseline + PLANT, CD_minus = CD_baseline -> "
                                "the derivative is PLANT / (2 x CTRL_STEP) EXACTLY and independently "
                                "of CD_baseline.  A reader that cannot return it has not been shown "
                                "able to see a non-zero."}}


def check_ctrl_not_confusable(rows, ctrl):
    """THE OTHER DIRECTION OF THE CONTROL, AND IT IS NOT CEREMONY: a collision between a
    measured derivative and either control value is an AMBIGUITY, and an ambiguity is
    refused rather than disclosed in a footnote.  Also refuses if the control's namespace
    is not disjoint from the design variables."""
    if CTRL_NAME in DVS or any(dv == CTRL_NAME for dv, _ in COMPONENTS):
        refuse("CTRL", {"control_namespace_not_disjoint": CTRL_NAME, "DVS": list(DVS)})
    want = PLANT / (2.0 * CTRL_STEP)
    hits = []
    for row in rows:
        if row.get("dv") == CTRL_NAME:
            continue
        if row.get("status") == "CONTROL":
            hits.append({"why": "a non-CTRL row carries status CONTROL", "dv": row.get("dv"), "idx": row.get("idx")})
            continue
        for key, v in (row.get("fd") or {}).items():
            if not v.get("ok"):
                continue
            for comp in ("dCD", "dCL"):
                val = float(v[comp])
                if val == 0.0:
                    hits.append({"why": "a MEASURED derivative is EXACTLY 0.0, the CTRL zero-arm value",
                                 "dv": row.get("dv"), "idx": row.get("idx"), "step": key, "component": comp})
                elif abs(val - want) <= 1e-15 * abs(want):
                    hits.append({"why": "a MEASURED derivative equals the CTRL planted constant",
                                 "dv": row.get("dv"), "idx": row.get("idx"), "step": key,
                                 "component": comp, "value": val, "ctrl_planted": want})
    if hits:
        refuse("CTRL", {"measured_row_collides_with_the_control": hits,
                        "note": "the control's job is to be unmistakable; a collision is REFUSED, not "
                                "annotated"})
    zero = float(ctrl["fd"][repr(CTRL_STEP)]["dCD"])
    plant = float(ctrl["planted"]["dCD"])
    if zero != 0.0 or abs(plant - want) > 1e-12 * abs(want):
        refuse("CTRL", {"control_row_does_not_carry_its_own_constants": {"zero": zero, "planted": plant,
                                                                         "want": want}})
    return {"ctrl_zero": zero, "ctrl_planted": plant, "want": want, "collisions": 0}


def build_F_record(level, nprocs, ident, points_md5, adjoint_src, cd0, cl0, eta, rows, extra,
                   components=None, trivial_step=None):
    comps = COMPONENTS if components is None else components
    triv = TRIVIAL_STEP if trivial_step is None else trivial_step
    return {"item": ITEM, "mode": "F", "level": level, "nprocs": int(nprocs),
            "identity": ident, "points_md5": points_md5,
            # LIST OF [str,int] LISTS, equal to d8g_grade.COMPONENTS_REGISTERED or read_F refuses
            "components_requested": [[dv, int(idx)] for dv, idx in comps],
            "n_components_requested": len(comps),
            "steps": list(STEPS["twist"]), "steps_by_dv": {k: list(v) for k, v in STEPS.items()},
            "trivial_step": triv,                           # 1.0e-3 to within 1e-15 or read_F refuses
            "adjoint_source": adjoint_src,
            "CD_baseline": _num(cd0), "CL_baseline": _num(cl0),
            "eta_used": _num(eta),
            "ctrl_step": CTRL_STEP, "plant": PLANT,
            "components_untouched_by_name": dict(UNTOUCHED_BY_NAME),
            "rows": rows, "n_rows": len(rows), **extra}


# ================= atomic write + READ-BACK ===========================================
def write_json_fsync(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    return md5_of(path)


def verify_written_F(path):
    """THE WRITTEN ARTEFACT IS READ BACK FROM DISK AND THE CONTROL IS RECOVERED THROUGH THE
    COMPARATOR'S OWN ARITHMETIC.  D8R re-read its JSONL; the comparator reads the .json, so
    this re-reads the .json -- the file that will actually be graded.  Every clause below is
    one the comparator itself will apply, moved forward to where it costs nothing."""
    j = json.load(open(path))
    if j.get("components_requested") != [[dv, int(idx)] for dv, idx in COMPONENTS]:
        refuse("READBACK", {"components_requested_not_registered": j.get("components_requested")})
    if j.get("trivial_step") is None or abs(float(j["trivial_step"]) - TRIVIAL_STEP) > 1e-15:
        refuse("READBACK", {"trivial_step_not_registered": j.get("trivial_step"), "registered": TRIVIAL_STEP})
    src = (j.get("adjoint_source") or {}).get("md5")
    if not (isinstance(src, str) and re.fullmatch(r"[0-9a-f]{32}", src)):
        refuse("READBACK", {"adjoint_source_md5_not_an_md5": src,
                            "note": "the FD table must be provably beside THIS row's adjoint"})
    want_steps = set(STEPS["twist"]) | {TRIVIAL_STEP}
    ctrl, seen = None, {}
    for row in j.get("rows") or []:
        if row.get("dv") == CTRL_NAME:
            ctrl = row
            continue
        seen[(row.get("dv"), int(row.get("idx")))] = {float(v["step"]) for v in (row.get("fd") or {}).values()}
    missing = []
    for dv, idx in COMPONENTS:
        got = seen.get((dv, idx))
        if got is None:
            missing.append({"component": "%s[%d]" % (dv, idx), "why": "row absent"})
        elif not want_steps.issubset(got):
            missing.append({"component": "%s[%d]" % (dv, idx), "steps_missing": sorted(want_steps - got)})
    if missing:
        refuse("READBACK", {"registered_components_or_steps_missing": missing,
                            "note": "the comparator's trivial baseline REFUSES below 3 components at "
                                    "the trivial step; a table that cannot be graded is not written"})
    if ctrl is None:
        refuse("READBACK", {"ctrl_row_absent_from_written_artefact": path})
    zero = float(ctrl["fd"][repr(CTRL_STEP)]["dCD"])
    plant = float(ctrl["planted"]["dCD"])
    want = PLANT / (2.0 * CTRL_STEP)
    if zero != 0.0 or abs(plant - want) > 1e-12 * abs(want):
        refuse("READBACK", {"planted_zero_control_not_recovered_from_disk": {"zero": zero, "planted": plant,
                                                                             "want": want, "file": path}})
    return {"read_back_from": path, "ctrl_zero": zero, "ctrl_planted": plant, "want": want,
            "n_rows": len(j.get("rows") or [])}


def verify_written_P(path, level, cells):
    j = json.load(open(path))
    bad = []
    if not isinstance(j.get("cells"), int) or j["cells"] != int(cells):
        bad.append({"cells": j.get("cells"), "type": type(j.get("cells")).__name__, "measured": int(cells)})
    if not isinstance(j.get("nprocs"), int):
        bad.append({"nprocs": j.get("nprocs"), "type": type(j.get("nprocs")).__name__})
    if j.get("level") != level:
        bad.append({"level": j.get("level"), "expected": level})
    for k in ("CD", "CL"):
        try:
            float(j[k])
        except (KeyError, TypeError, ValueError):
            bad.append({"unreadable": k, "value": j.get(k)})
    if bad:
        refuse("READBACK", {"P_artefact_will_not_read": bad, "file": path})
    return {"read_back_from": path, "cells": j["cells"], "level": j["level"]}


def verify_written_A(path, level):
    j = json.load(open(path))
    bad = []
    if j.get("level") != level:
        bad.append({"level": j.get("level"), "expected": level})
    if not isinstance(j.get("nprocs"), int):
        bad.append({"nprocs": j.get("nprocs")})
    need_idx = max(i for _, i in COMPONENTS)
    for of in ("CD", "CL"):
        for dv in DVS:
            try:
                arr = j["adjoint"][of][dv]
                _ = [float(v) for v in arr]
            except Exception as exc:                          # noqa: BLE001
                bad.append({"adjoint_unreadable": [of, dv], "error": repr(exc)[:200]})
                continue
            if dv == "twist" and len(arr) <= need_idx:
                bad.append({"adjoint_too_short": [of, dv], "n": len(arr), "need_index": need_idx})
    for k in ("CD_baseline", "CL_baseline"):
        try:
            float(j[k])
        except (KeyError, TypeError, ValueError):
            bad.append({"unreadable": k, "value": j.get(k)})
    if bad:
        refuse("READBACK", {"A_artefact_will_not_read": bad, "file": path})
    return {"read_back_from": path, "level": j["level"]}


# ================= the age datum and the mesh, checked for immutability ===============
def read_age_datum(root):
    p = os.path.join(root, AGE_DATUM_FILE)
    ref = os.path.join(root, AGE_DATUM_REF)
    if not os.path.isfile(p) or not os.path.isfile(ref):
        return None
    try:
        return {"datum": int(open(p).read().strip()), "ref": ref}
    except ValueError:
        return None


def age_datum_moved(rec):
    """G1's age guard REFUSES an arm whose `0/U` mtime no longer equals the staged datum --
    pyDAFoam writes the primal end state back into time 0, so this is a live hazard, and it
    would otherwise surface only at grading time as an unexplained refusal.  MEASURED on
    the D8R graded arm: 0/U mtime == the datum, unmoved across a 16-minute np=4 run, so the
    hazard does not fire on this family in practice -- which is exactly why it must be
    checked rather than assumed."""
    if rec is None:
        return None
    return int(os.path.getmtime(rec["ref"])) != rec["datum"]


# ================= stdout: every line is prefixed and none may look like the solver ====
GRADER_LOG_PATTERNS = (r"^\s*primalMinResTol\s+([0-9.eE+-]+)\s*;",
                       r"^\s*primalMinResTolDiff\s+([0-9.eE+-]+)\s*;",
                       r"^(U0|U1|U2|he|p|nuTilda)\s+initRes:\s+([0-9.eE+-]+)",
                       r"^Time = ",
                       r"^Running Primal Solver",
                       r"^CD:\s+([0-9.eE+-]+)",
                       r"^CL:\s+([0-9.eE+-]+)")


def d8g_line(line):
    """Build the instrument's own stdout line.  EVERY line starts with `D8G_`.  The
    comparator's G-PRIMAL and G-PLAT read the SOLVER'S OWN stdout; a producer line that
    parsed as solver output would be forged evidence.  Split out from says() so the
    selftest can check the exact bytes without capturing a stream."""
    return line if line.startswith("D8G_") else "D8G_" + line


def says(line):
    sys.stdout.write(d8g_line(line))
    sys.stdout.write("\n")
    sys.stdout.flush()


def lines_are_clean(lines):
    """Returns the list of (pattern, line) pairs where an instrument line would be parsed
    as solver output.  EMPTY IS THE ONLY ACCEPTABLE ANSWER."""
    bad = []
    for pat in GRADER_LOG_PATTERNS:
        rex = re.compile(pat, re.M)
        for ln in lines:
            if rex.search(ln):
                bad.append((pat, ln))
    return bad


# ================= main ===============================================================
def main(argv):
    mode, level = parse_args(argv)
    if mode is None:
        sys.stderr.write("D8G_OF usage: d8g_of.py -mode P|A|F -level L1|L2|L3  "
                         "(modes A and F are registered at %s only)\n" % FD_LEVEL)
        return 64

    ok, got, why = check_producer_md5(PRODUCER, PRODUCER_MD5)
    if not ok:
        sys.stderr.write("D8G_OF REFUSE producer: %s\n" % why)
        return 2

    with open(PRODUCER) as fh:
        src = fh.read()
    if src.count(ANCHOR) != 1:
        sys.stderr.write("D8G_OF REFUSE anchor %r appears %d times in %s\n" % (ANCHOR, src.count(ANCHOR), PRODUCER))
        return 2
    header = src.split(ANCHOR)[0]

    root = os.getcwd()
    # ---- everything that can refuse BEFORE a core-minute is spent, refuses here -------
    try:
        cells_rec = measure_cells(os.path.join(root, POLYMESH))
        cdict = read_controldict(os.path.join(root, CONTROLDICT))
        bad_cd = check_registered_controldict(cdict)
        if bad_cd:
            refuse("CONTROLDICT", {"departures_from_the_registered_controlDict": bad_cd})
        if not os.path.isfile(os.path.join(root, POINTS)):
            refuse("MESH", {"points_absent": POINTS,
                            "note": "the comparator's G-M2 hashes exactly this path per arm"})
        points_md5_pre = md5_of(os.path.join(root, POINTS))
    except Refusal as exc:
        sys.stderr.write("D8G_OF REFUSE %s\n" % exc)
        return 2
    if cells_rec["cells"] != CELLS_REGISTERED[level]:
        sys.stderr.write("D8G_OF REFUSE the mesh in this arm has %d cells; level %s is registered at %d "
                         "(the comparator REFUSES on exactly this and the arm would be spent first)\n"
                         % (cells_rec["cells"], level, CELLS_REGISTERED[level]))
        return 2

    age = read_age_datum(root)
    says("AGE_DATUM %s" % json.dumps({"present": age is not None,
                                      "datum": (age or {}).get("datum"),
                                      "ref": AGE_DATUM_REF}, sort_keys=True))
    says("MESH_MEASURED %s" % json.dumps(dict(cells_rec, level=level, registered=CELLS_REGISTERED[level]),
                                         sort_keys=True))

    saved_argv = list(sys.argv)
    sys.argv = [PRODUCER, "-task", "run_model", "-optimizer", "IPOPT"]
    ns = {"__name__": "d8g_frozen_header", "__file__": PRODUCER}
    exec(compile(header, PRODUCER, "exec"), ns)
    sys.argv = saved_argv

    daOptions = ns["daOptions"]
    bad_do = check_registered_daoptions(daOptions)
    if bad_do:
        sys.stderr.write("D8G_OF REFUSE daOptions departs from the registered set %s\n"
                         % json.dumps(bad_do, sort_keys=True, default=str))
        return 2
    # THE PAIR IS REPORTED IN THIS INSTRUMENT'S OWN SYNTAX, NEVER THE SOLVER'S: G-PRIMAL
    # must read it back from DAFoam's own daOption dump, not from a line this file wrote.
    says(daoptions_report_line(daOptions))

    fc = forecast_plateau_window(cdict["endTime"], cdict["deltaT"], daOptions["printInterval"])
    says("PLATEAU_WINDOW_FORECAST %s" % json.dumps(fc, sort_keys=True))
    if not fc["sufficient"]:
        sys.stderr.write("D8G_OF REFUSE the forecast plateau window holds %d < %d samples: G-PLAT would "
                         "make this level NOT A RESULT FOR WANT OF EVIDENCE and the arm would be spent "
                         "first\n" % (fc["plateau_window_expected"], PLATEAU_MIN_SAMPLES))
        return 2

    from mpi4py import MPI
    import numpy as np
    import openmdao.api as om

    rank = MPI.COMM_WORLD.rank
    nprocs = MPI.COMM_WORLD.size
    Top = ns["Top"]
    jsonl = JSONL[mode]

    def emit(rec):
        if rank != 0:
            return
        with open(jsonl, "a") as fh:
            fh.write(json.dumps(rec, sort_keys=True, default=str) + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    ident = idwarp_identity()
    not_measured = []
    if ident.get("libidwarp_so_md5") is None:
        not_measured.append({"field": "identity.libidwarp_so_md5", "why": ident.get("error"),
                             "class": "INFRASTRUCTURE (L-342): disclosed, never filled, never composed; "
                                      "the comparator's G9 decides what it means"})
    if cells_rec["cells_from_owner_body_max_plus_1"] == NOT_MEASURED:
        not_measured.append({"field": "cells cross-check (owner body)", "why": "mesh not in format ascii",
                             "class": "INFRASTRUCTURE (L-342): the cell count itself is MEASURED from the "
                                      "header note; only the second, independent reader is unavailable"})

    emit({"kind": "identity", "item": ITEM, "mode": mode, "level": level, "nprocs": nprocs,
          "producer_md5": got, "solverName": daOptions.get("solverName"),
          "primalMinResTol": daOptions.get("primalMinResTol"),
          "primalMinResTolDiff": daOptions.get("primalMinResTolDiff"),
          "printInterval": daOptions.get("printInterval"),
          "controlDict": cdict, "plateau_window_forecast": fc,
          "cells": cells_rec, "points_md5": points_md5_pre,
          "not_measured": not_measured, **ident})

    prob = om.Problem()
    prob.model = Top()
    prob.setup(mode="rev")

    CD_K = "%s.aero_post.CD" % SCENARIO
    CL_K = "%s.aero_post.CL" % SCENARIO

    def dvs_now():
        return {k: [float(v) for v in np.atleast_1d(np.array(prob.get_val(k), dtype=float))] for k in DVS}

    def primal(tag):
        t0 = time.time()
        prob.run_model()
        cd = float(prob.get_val(CD_K)[0])
        cl = float(prob.get_val(CL_K)[0])
        emit({"kind": "primal", "tag": tag, "CD": _num(cd), "CL": _num(cl),
              "wall_s": round(time.time() - t0, 3)})
        return cd, cl

    def finish(mode_, record, verifier):
        """Write, fsync, READ BACK, then and only then print the terminal marker.  The
        marker is the comparator's completion evidence and is never printed on a path that
        did not complete.  THE MESH AND THE AGE DATUM ARE RE-CHECKED HERE: if either moved,
        the artefact is still written -- it is evidence and a human will want it -- but the
        TERMINAL MARKER IS WITHHELD, so G1 refuses the arm instead of grading a run whose
        cold-start proof is void."""
        if rank != 0:
            MPI.COMM_WORLD.Barrier()
            return 0
        path = OUT[mode_]
        art_md5 = write_json_fsync(path, record)
        rb = verifier()
        says("ARTEFACT_READ_BACK %s" % json.dumps(dict(rb, md5=art_md5), sort_keys=True, default=str))
        moved_mesh = md5_of(os.path.join(root, POINTS)) != points_md5_pre
        moved_age = age_datum_moved(age)
        if moved_mesh:
            sys.stderr.write("D8G_OF MESH_MOVED constant/polyMesh/points.gz changed during the run; "
                             "G-M2 would refuse this arm.  ARTEFACT WRITTEN, TERMINAL MARKER WITHHELD.\n")
            return 2
        if moved_age:
            sys.stderr.write("D8G_OF AGE_DATUM_MOVED 0/U mtime no longer equals the staged datum; the "
                             "cold-start proof is void and G1 would refuse.  ARTEFACT WRITTEN, TERMINAL "
                             "MARKER WITHHELD.\n")
            return 2
        says("%s %s" % (TERMINAL[mode_], path))
        return 0

    # ---------------- MODE P: exactly ONE cold primal at this level -------------------
    # EXACTLY ONE, and that is load-bearing: the comparator grades the LAST `Running
    # Primal Solver` segment, so a warm-up or a repeat here would silently move the graded
    # history to a different primal.
    if mode == "P":
        cd, cl = primal("cold")
        rec = build_P_record(level, cells_rec, nprocs, ident, points_md5_pre, cdict, cd, cl,
                             {"not_measured": not_measured, "plateau_window_forecast": fc,
                              "dvs": dvs_now(), "n_primals_in_this_arm": 1,
                              "n_primals_note": "EXACTLY ONE: the comparator grades the LAST primal "
                                                "segment of the arm log"})
        rc = finish("P", rec, lambda: verify_written_P(OUT["P"], level, cells_rec["cells"]))
        if rank == 0:
            MPI.COMM_WORLD.Barrier()
        return rc

    # ---------------- MODE A: the L2 adjoint at the BASELINE design -------------------
    if mode == "A":
        cd, cl = primal("baseline")
        t0 = time.time()
        totals = prob.compute_totals(of=[CD_K, CL_K], wrt=list(DVS))
        emit({"kind": "compute_totals", "wall_s": round(time.time() - t0, 3)})
        jadj = {}
        for of_key_full, of_key in ((CD_K, "CD"), (CL_K, "CL")):
            jadj[of_key] = {}
            for dv in DVS:
                arr = np.atleast_1d(np.array(totals[(of_key_full, dv)]).ravel())
                jadj[of_key][dv] = [_num(v) for v in arr]
                emit({"kind": "adjoint", "of": of_key, "dv": dv, "n": int(arr.size),
                      "values": jadj[of_key][dv]})
        rec = build_A_record(level, nprocs, ident, points_md5_pre, cd, cl, jadj,
                             {"not_measured": not_measured, "dvs": dvs_now(),
                              "design_point": "BASELINE -- this item runs no optimiser, so the adjoint "
                                              "and the FD table sit at the SAME design on both rows",
                              "no_gradient_triple": "section 7: the adjoint is BLOCKED at L3 on memory "
                                                    "AND, independently, on conditioning.  This arm is "
                                                    "the L2 row of a pair, not a triple, and no order "
                                                    "of accuracy is claimed for the gradient."})
        rc = finish("A", rec, lambda: verify_written_A(OUT["A"], level))
        if rank == 0:
            MPI.COMM_WORLD.Barrier()
        return rc

    # ---------------- MODE F: the L2 central-FD table beside THIS ROW's adjoint -------
    if not os.path.isfile(GRADIENT_IN):
        sys.stderr.write("D8G_OF REFUSE gradient file %s absent (d8g_run_arm.sh copies the SAME ROW's "
                         "A arm d8g_A.json here)\n" % GRADIENT_IN)
        return 2
    ep = json.load(open(GRADIENT_IN))
    ep_md5 = md5_of(GRADIENT_IN)
    bad_src = []
    if ep.get("item") != ITEM or ep.get("mode") != "A":
        bad_src.append({"not_a_D8G_mode_A_artefact": {"item": ep.get("item"), "mode": ep.get("mode")}})
    if ep.get("level") != FD_LEVEL:
        bad_src.append({"gradient_is_not_at_the_registered_level": ep.get("level"), "registered": FD_LEVEL})
    ep_so = (ep.get("identity") or {}).get("libidwarp_so_md5")
    my_so = ident.get("libidwarp_so_md5")
    if ep_so is not None and my_so is not None and ep_so != my_so:
        # THE ROW IS THE TOOLCHAIN AND THE TOOLCHAIN IS THE HASH (DAFOAM_CHARTER section 11).
        # The comparator binds the F table to the A artefact by md5; this binds it to the
        # SAME ROW before the compute, so a cross-row stage is caught in seconds, not hours.
        bad_src.append({"gradient_came_from_the_OTHER_TOOLCHAIN_ROW": {"gradient_so_md5": ep_so,
                                                                       "this_arm_so_md5": my_so}})
    if bad_src:
        sys.stderr.write("D8G_OF REFUSE staged gradient %s\n" % json.dumps(bad_src, sort_keys=True, default=str))
        return 2
    says("GRADIENT_STAGED %s" % json.dumps({"file": GRADIENT_IN, "md5": ep_md5, "level": ep.get("level"),
                                            "so_md5": ep_so}, sort_keys=True))
    emit({"kind": "gradient_loaded", "file": GRADIENT_IN, "md5": ep_md5, "level": ep.get("level"),
          "CD_baseline_A": ep.get("CD_baseline"), "so_md5": ep_so})

    base = {k: np.atleast_1d(np.array(prob.get_val(k), dtype=float)).copy() for k in DVS}
    emit({"kind": "baseline_dvs", "dvs": {k: [_num(v) for v in base[k]] for k in DVS}})

    cd0, cl0 = primal("baseline")
    cd0r, cl0r = primal("baseline_repeat")
    eta_raw = abs(cd0 - cd0r)
    eta_flagged = bool(eta_raw < ETA_FLOOR)
    eta = ETA_FLOOR if eta_flagged else eta_raw
    emit({"kind": "eta", "eta_raw": _num(eta_raw), "eta_used": _num(eta), "eta_floored": eta_flagged,
          "CD_baseline": _num(cd0), "CD_repeat": _num(cd0r), "CL_baseline": _num(cl0), "CL_repeat": _num(cl0r)})

    def probe(dv, idx, delta):
        for k in DVS:
            prob.set_val(k, base[k].copy())
        v = base[dv].copy()
        v[idx] += delta
        prob.set_val(dv, v)
        return primal("%s[%d]%+g" % (dv, idx, delta))

    # THE TRIVIAL STEP IS EVALUATED TOO.  It is the section-4 baseline whose JOB IS TO FAIL:
    # if the deliberately wrong 1e-3 deg step also passes, the comparator WITHDRAWS the FD
    # verdict.  Four steps x five components x two primals + two baselines = 42 primals.
    step_set = fd_step_set()
    rows = []
    for dv, idx in COMPONENTS:
        if idx >= base[dv].size:
            rows.append({"dv": dv, "idx": idx, "status": "ABSENT", "n_available": int(base[dv].size), "fd": {}})
            continue
        rows.append(fd_row(probe, dv, idx, step_set, emit=emit))
    for k in DVS:
        prob.set_val(k, base[k].copy())

    ctrl = build_ctrl_row(cd0, cl0)
    coll = check_ctrl_not_confusable(rows, ctrl)
    emit({"kind": "control", "row": ctrl, "collision_check": coll})
    rows.append(ctrl)
    says("PLANTED_ZERO_CONTROL zero=%r planted=%r want=%r collisions=%d"
         % (coll["ctrl_zero"], coll["ctrl_planted"], coll["want"], coll["collisions"]))

    rec = build_F_record(level, nprocs, ident, points_md5_pre,
                         {"file": GRADIENT_IN, "md5": ep_md5, "level": ep.get("level"),
                          "so_md5": ep_so,
                          "note": "the md5 of the SAME ROW's d8g_A.json, so this FD table is provably "
                                  "beside the adjoint it checks and not some other run's"},
                         cd0, cl0, eta, rows,
                         {"not_measured": not_measured,
                          "eta_raw": _num(eta_raw), "eta_floored": eta_flagged,
                          "CD_baseline_repeat": _num(cd0r), "CL_baseline_repeat": _num(cl0r),
                          "baseline_dvs": {k: [_num(v) for v in base[k]] for k in DVS},
                          "steps_evaluated": step_set,
                          "n_primals_in_this_arm": 2 + 2 * len(step_set) * len(COMPONENTS),
                          "trivial_step_note": "EVALUATED, NOT DECLARED: the 1e-3 deg step is the "
                                               "section-4 baseline whose job is to FAIL, and the "
                                               "comparator WITHDRAWS the FD verdict if it passes"})
    rc = finish("F", rec, lambda: verify_written_F(OUT["F"]))
    if rank == 0:
        MPI.COMM_WORLD.Barrier()
    return rc




# ================= SELFTEST: producer artefacts driven THROUGH THE COMPARATOR ==========
# THE POINT OF THIS SUITE, STATED ONCE.  A producer selftest that only checked its own
# output against its own expectations would be a mirror.  This one loads
# d8g_grade.py -- THE SPECIFICATION -- and feeds it artefacts built by the SAME
# builders main() uses, through the comparator's OWN read_P / read_A / read_F /
# functional_plant_control / ctrl_control / grader_plant_control / grade_components /
# _trivial_baseline.  A key the grader reads and the producer never writes fails HERE, for
# free, instead of at grading time after ten arms of compute.
#
# WHAT IT DOES NOT TEST, STATED PLAINLY: it does not test DAFoam, IDWarp, MPI, docker, a
# mesh or a solver.  Every probe is analytic and every fixture is synthetic.  A green here
# means THE ARTEFACT CONTRACT IS SATISFIED AND THE CONTROLS REFUSE WHAT THEY CLAIM TO
# REFUSE.  It does not mean any D8G arm has ever run.
#
# NOT COVERED, BY NAME, because they are not this instrument's output: the comparator's
# read_ledger (d8g_run_arm.sh writes the ledger), read_mesh_record (d8g_genmesh.sh writes
# the mesh records), and the four log readers read_primal_tolerances / read_max_init_res /
# read_functional_history / last_primal_segment (DAFoam writes the log).  This file's only
# duty toward those three is NEGATIVE -- to emit nothing that could be mistaken for them --
# and U19/U20 below test exactly that.

SELFTEST_GRADER = "d8g_grade.py"

# The synthetic case.  CD(x) = c0 + sum_i A_TWIST[i] * x_i, plus a DETERMINISTIC solver
# noise of amplitude SELF_ETA whose sign follows the sign of the perturbation, so the
# central difference is exactly  A_TWIST[i] + SELF_ETA * sigma_i / h.  That is the real
# shape of a step-size plateau: the error falls as 1/h, so the three registered steps
# plateau and the 1e-3 trivial step does not -- which is what section 4 REGISTERED the
# trivial baseline to demonstrate.
A_TWIST = [-2.3e-3, -2.0e-3, -1.7e-3, -1.3e-3, -8.6e-4, -1.1e-3, -2.0e-4]
A_PATCHV = [8.7e-4, 1.06e-2]
SELF_ETA = 1.0e-6
SELF_CD0 = 3.902498742395508e-02
SELF_CL0 = 5.0e-01
SELF_SIGMA = {0: 1.0, 1: -1.0, 2: 1.0, 3: -1.0, 4: 1.0, 5: -1.0, 6: 1.0}


def _self_probe(dv, idx, delta):
    """The analytic stand-in for one primal pair half.  No solver, no MPI, no mesh."""
    g = A_TWIST[idx] if dv == "twist" else A_PATCHV[idx]
    sgn = 1.0 if delta > 0 else -1.0
    cd = SELF_CD0 + g * delta + SELF_ETA * SELF_SIGMA[idx] * sgn
    cl = SELF_CL0 + 10.0 * g * delta + 10.0 * SELF_ETA * SELF_SIGMA[idx] * sgn
    return cd, cl


def _self_adjoint():
    return {of: {"twist": [_num(v * (10.0 if of == "CL" else 1.0)) for v in A_TWIST],
                 "patchV": [_num(v * (10.0 if of == "CL" else 1.0)) for v in A_PATCHV]}
            for of in ("CD", "CL")}


def _self_ident():
    return {"idwarp_file": "/x/idwarp/__init__.py",
            "libidwarp_so_md5": "85f59e87253e0a71a813f64ca6e4c425"}


def _self_owner(path, n_cells, note_cells=None, fmt="ascii"):
    """A synthetic constant/polyMesh/owner: a FoamFile header carrying the note, then the
    face-owner list.  `note_cells` lets a test PLANT a header that disagrees with the body."""
    n_faces = 3 * n_cells
    body = [str(i % n_cells) for i in range(n_faces)]
    txt = ('FoamFile\n{\n    version     2.0;\n    format      %s;\n'
           '    note        "nPoints:%d  nCells:%d  nFaces:%d  nInternalFaces:%d";\n'
           '    class       labelList;\n    object      owner;\n}\n'
           '// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n\n'
           '%d\n(\n%s\n)\n'
           % (fmt, n_cells * 2, (note_cells if note_cells is not None else n_cells),
              n_faces, n_faces - 6, n_faces, "\n".join(body)))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(txt)
    return path


def _self_controldict(path, end_time=1000, delta_t=1, stop_at="endTime"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version 2.0;\n    format ascii;\n    object controlDict;\n}\n"
                 "application     DARhoSimpleCFoam;\nstartFrom       startTime;\nstartTime  0;\n"
                 "stopAt          %s;\nendTime         %s;\ndeltaT          %s;\n"
                 "writeControl    timeStep;\nwriteInterval   250;\n" % (stop_at, end_time, delta_t))
    return path


def _self_build_F(tmp, tag, components=None, trivial=None, steps=None, wreck=None):
    """Build an F artefact with the PRODUCTION builders -- fd_row, build_ctrl_row,
    build_F_record, write_json_fsync -- and return its path.  `wreck` mutates the record
    so a control can be seen to fire."""
    comps = components if components is not None else COMPONENTS
    triv = TRIVIAL_STEP if trivial is None else trivial
    step_set = fd_step_set() if steps is None else sorted(steps)
    if trivial is not None:
        step_set = sorted(set(STEPS["twist"]) | {triv})
    d = os.path.join(tmp, "F_" + tag)
    os.makedirs(d, exist_ok=True)
    apath = os.path.join(d, "d8g_A_gradient.json")
    write_json_fsync(apath, {"item": ITEM, "mode": "A", "level": FD_LEVEL, "nprocs": 4,
                             "identity": _self_ident(), "points_md5": "0" * 32,
                             "CD_baseline": _num(SELF_CD0), "CL_baseline": _num(SELF_CL0),
                             "adjoint": _self_adjoint()})
    rows = [fd_row(_self_probe, dv, idx, step_set) for dv, idx in comps]
    ctrl = build_ctrl_row(SELF_CD0, SELF_CL0)
    rows.append(ctrl)
    rec = build_F_record(FD_LEVEL, 4, _self_ident(), "0" * 32,
                         {"file": "d8g_A_gradient.json", "md5": md5_of(apath), "level": FD_LEVEL},
                         SELF_CD0, SELF_CL0, 1.08e-5, rows, {}, components=comps, trivial_step=triv)
    if wreck:
        wreck(rec)
    fpath = os.path.join(d, "d8g_F.json")
    write_json_fsync(fpath, rec)
    return fpath, apath


def _self_build_P(tmp, tag, cells=44544, wreck=None):
    d = os.path.join(tmp, "P_" + tag)
    os.makedirs(d, exist_ok=True)
    cells_rec = {"cells": cells, "cells_from_owner_header_note": cells,
                 "cells_from_owner_body_max_plus_1": cells, "owner_file": "synthetic",
                 "readers_agree": True}
    rec = build_P_record("L2", cells_rec, 4, _self_ident(), "0" * 32,
                         {"endTime": 1000.0, "deltaT": 1.0, "stopAt": "endTime", "writeInterval": 250.0},
                         SELF_CD0, SELF_CL0, {})
    if wreck:
        wreck(rec)
    p = os.path.join(d, "d8g_P.json")
    write_json_fsync(p, rec)
    return p


def _load_grader(here):
    # `here` is the directory the comparator is looked for in.  A mutated copy of this file
    # runs from a scratch directory, so the harness passes --specdir: WITHOUT IT THE MUTATED
    # COPY WOULD FAIL FOR THE WRONG REASON (comparator absent) AND THE MUTATION CONTROL
    # WOULD REPORT A CATCH IT DID NOT MAKE.
    import importlib.machinery
    import importlib.util
    # NO BYTECODE CACHE.  Loading `d8g_grade.py` by loader caches it as
    # `__pycache__/d8g_grade.py.cpython-*.pyc`, and a STALE cache is exactly the failure
    # that inverts a mutation suite -- the clean control fails and the mutated case passes.
    # It also drops build clutter into a CASE directory, where nothing but the case belongs.
    sys.dont_write_bytecode = True
    path = os.path.join(here, SELFTEST_GRADER)
    if not os.path.isfile(path):
        return None, path
    loader = importlib.machinery.SourceFileLoader("d8g_grade_spec", path)
    spec = importlib.util.spec_from_loader("d8g_grade_spec", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod, path


def _try(fn, default=None):
    """Evaluate fn(), or return `default` if it refuses.  Positive units use this so a
    REFUSAL marks the named unit BAD and the suite CONTINUES -- without it a refusal inside
    a unit expression aborts the run, and a mutation control then sees a non-zero exit with
    NO NAMED CATCHER and cannot tell a fired gate from a crash."""
    try:
        return fn()
    except Exception:                                          # noqa: BLE001
        return default


def _raises(fn):
    """True if fn() raises -- used only to drive a REFUSAL path.  The comparator raises its
    own Refusal type, this module raises its own; both are caught the same way."""
    try:
        fn()
    except Exception:                                          # noqa: BLE001
        return True
    return False


def selftest(tmp, here):
    n = 0
    fails = []

    def unit(name, cond):
        nonlocal n
        n += 1
        if not cond:
            fails.append(name)
        print("  [%s] %s" % ("OK " if cond else "BAD", name))

    G, gpath = _load_grader(here)
    if G is None:
        print("REFUSE the comparator %s is not beside this file; the producer's whole duty is "
              "conformance to it and a suite that cannot load it proves nothing" % gpath)
        return 2
    print("  spec = %s  md5 = %s" % (gpath, md5_of(gpath)))

    # ---- A. the command line and the frozen-producer refusal ------------------------
    unit("U1 parse_args accepts -mode P -level L1",
         parse_args(["x", "-mode", "P", "-level", "L1"]) == ("P", "L1"))
    unit("U2 parse_args REFUSES mode A away from the registered FD level",
         parse_args(["x", "-mode", "A", "-level", "L1"]) == (None, None))
    unit("U3 parse_args REFUSES an unregistered mode",
         parse_args(["x", "-mode", "O", "-level", "L2"]) == (None, None))
    # U4 WAS "refuses while the token stands".  The token is gone (2026-09-11), so the unit is
    # INVERTED into the property that replaced it: the pinned constant must be the frozen
    # three-way md5 AND the producer script actually sitting beside this file must hash to it.
    # A pinned constant nobody checks against the real file is a hash that describes nothing.
    # The dual-spelling search this unit carried until 2026-09-11 existed so U4 would
    # survive the freeze rename.  The rename has happened; a branch that can never be taken
    # again reads like a live possibility and is removed.
    _p = os.path.join(here, "d8g_runScript.py")
    _rs = _p if os.path.isfile(_p) else None
    unit("U4 PRODUCER_MD5 is PINNED to the frozen D8 -> D8R -> D8G md5 AND the producer script "
         "beside this file hashes to it",
         PRODUCER_MD5 == "28c7819487a025a5f6554d38062a2b66"
         and _rs is not None and md5_of(_rs) == PRODUCER_MD5)
    unit("U5 check_producer_md5 accepts a file that hashes to the registered md5",
         check_producer_md5(__file__, md5_of(__file__))[0] is True)
    unit("U6 check_producer_md5 REFUSES a file that does not",
         check_producer_md5(__file__, "0" * 32)[0] is False)

    # ---- B. the mesh readers, and the planted disagreement between them --------------
    ow = _self_owner(os.path.join(tmp, "mesh_ok", "constant", "polyMesh", "owner"), 5568)
    unit("U7 read_cells_from_note sees the planted nCells", read_cells_from_note(ow) == 5568)
    unit("U8 read_cells_from_owner_body sees it INDEPENDENTLY (max(owner)+1)",
         read_cells_from_owner_body(ow) == 5568)
    unit("U9 measure_cells returns the MEASURED count when both readers agree",
         measure_cells(os.path.dirname(ow))["cells"] == 5568)
    _self_owner(os.path.join(tmp, "mesh_liar", "constant", "polyMesh", "owner"), 5568, note_cells=44544)
    unit("U10 measure_cells REFUSES a header note that disagrees with the mesh body",
         _raises(lambda: measure_cells(os.path.join(tmp, "mesh_liar", "constant", "polyMesh"))))
    os.makedirs(os.path.join(tmp, "mesh_gone", "constant", "polyMesh"), exist_ok=True)
    unit("U11 measure_cells REFUSES an absent owner (PHYSICS absent -> REFUSE, L-342)",
         _raises(lambda: measure_cells(os.path.join(tmp, "mesh_gone", "constant", "polyMesh"))))
    nb = _self_owner(os.path.join(tmp, "mesh_bin", "constant", "polyMesh", "owner"), 5568, fmt="binary")
    unit("U12 the body cross-check returns None (NOT_MEASURED) on a non-ascii mesh, never a guess",
         read_cells_from_owner_body(nb) is None and read_cells_from_note(nb) == 5568)

    # ---- C. the acceptance pair and THE PLATEAU-WINDOW FORECAST ----------------------
    cdp = _self_controldict(os.path.join(tmp, "cdok", "system", "controlDict"))
    cd = read_controldict(cdp)
    unit("U13 read_controldict reads endTime/deltaT/stopAt",
         cd["endTime"] == 1000.0 and cd["deltaT"] == 1.0 and cd["stopAt"] == "endTime")
    unit("U14 check_registered_controldict is EMPTY on the registered dict", check_registered_controldict(cd) == [])
    cd2 = read_controldict(_self_controldict(os.path.join(tmp, "cdbad", "system", "controlDict"), end_time=500))
    unit("U15 check_registered_controldict flags endTime 500", len(check_registered_controldict(cd2)) == 1)
    unit("U16 check_registered_daoptions is EMPTY on the registered set",
         check_registered_daoptions(dict(REGISTERED_DAOPTIONS)) == [])
    tut = dict(REGISTERED_DAOPTIONS, primalMinResTolDiff=100.0)
    unit("U17 check_registered_daoptions flags the A6 TUTORIAL's OTHER primalMinResTolDiff (100)",
         [b["key"] for b in check_registered_daoptions(tut)] == ["primalMinResTolDiff"])
    unit("U18 printed_sample_count == 101 at endTime 1000 / deltaT 1 / printInterval 10 "
         "(MEASURED against the D8R arm log's last primal segment)",
         printed_sample_count(1000, 1, 10) == 101)
    unit("U19 plateau_window_size(101) == 11 and clears the floor of 10",
         plateau_window_size(101) == 11 and plateau_window_size(101) >= PLATEAU_MIN_SAMPLES)
    unit("U20 the forecast mirrors the comparator's own window function exactly",
         all(plateau_window_size(k) == len(G.plateau_window(list(range(k)))) for k in (10, 11, 37, 101, 3232)))
    unit("U21 the forecast REFUSES printInterval 200 (window 6 < 10: NOT A RESULT FOR WANT OF EVIDENCE)",
         forecast_plateau_window(1000, 1, 200)["sufficient"] is False)
    unit("U22 the forecast ACCEPTS the registered 1000/1/10", forecast_plateau_window(1000, 1, 10)["sufficient"] is True)

    # ---- D. STDOUT HYGIENE: the instrument may not forge the solver's own evidence ---
    emitted = [d8g_line("AGE_DATUM {}"), d8g_line("MESH_MEASURED {}"),
               d8g_line(daoptions_report_line(dict(REGISTERED_DAOPTIONS))),
               d8g_line("PLATEAU_WINDOW_FORECAST {}"), d8g_line("GRADIENT_STAGED {}"),
               d8g_line("ARTEFACT_READ_BACK {}"), d8g_line("PLANTED_ZERO_CONTROL zero=0.0 planted=0.00617"),
               d8g_line("P_WRITTEN d8g_P.json"), d8g_line("A_WRITTEN d8g_A.json"),
               d8g_line("F_WRITTEN d8g_F.json")]
    unit("U23 every line this instrument prints is D8G_-prefixed AND none parses as the "
         "SOLVER'S own output",
         lines_are_clean(emitted) == [] and all(ln.startswith("D8G_") for ln in emitted))
    forged = ["    primalMinResTol 1e-08;", "nuTilda initRes: 9.876e-03 finalRes: 1e-09", "CD: 0.038"]
    unit("U24 lines_are_clean CATCHES a forged solver line (the control that proves U23 is not ceremony)",
         len(lines_are_clean(forged)) >= 3)

    # ---- E. THE P ARTEFACT, THROUGH THE COMPARATOR'S OWN read_P ---------------------
    ppath = _self_build_P(tmp, "ok")
    rp = _try(lambda: G.read_P(ppath))
    unit("U25 comparator read_P reads the producer's P artefact (level, cells, CD, CL, so_md5, points_md5)",
         rp is not None and rp["level"] == "L2" and rp["cells"] == 44544
         and abs(rp["CD"] - SELF_CD0) < 1e-15
         and rp["so_md5"] == _self_ident()["libidwarp_so_md5"] and rp["nprocs"] == 4)
    unit("U26 `cells` and `nprocs` are INTEGERS -- the comparator compares them with != and a "
         "string would REFUSE",
         isinstance(json.load(open(ppath))["cells"], int) and isinstance(json.load(open(ppath))["nprocs"], int))
    unit("U27 comparator functional_plant_control SEES the CD plant in the producer's P artefact",
         _try(lambda: G.functional_plant_control(tmp, ppath, "selftest")["functional_plant_seen"]) is True)
    unit("U28 verify_written_P REFUSES a P artefact whose cells was written as a string",
         _raises(lambda: verify_written_P(_self_build_P(tmp, "strcells",
                                                        wreck=lambda r: r.__setitem__("cells", "44544")),
                                          "L2", 44544)))

    # ---- F. THE A ARTEFACT, THROUGH THE COMPARATOR'S OWN read_A ---------------------
    apath2 = os.path.join(tmp, "A_ok.json")
    write_json_fsync(apath2, build_A_record(FD_LEVEL, 4, _self_ident(), "0" * 32, SELF_CD0, SELF_CL0,
                                            _self_adjoint(), {}))
    ra = _try(lambda: G.read_A(apath2))
    unit("U29 comparator read_A reads BOTH objectives and BOTH design variables",
         ra is not None and set(ra["adjoint"]) == {"CD", "CL"} and len(ra["adjoint"]["CD"]["twist"]) == 7
         and len(ra["adjoint"]["CL"]["patchV"]) == 2 and abs(ra["CD"] - SELF_CD0) < 1e-15)
    unit("U30 the twist array is long enough for every registered component index",
         ra is not None and all(i < len(ra["adjoint"]["CD"]["twist"]) for _, i in COMPONENTS))

    # ---- G. THE F ARTEFACT, THROUGH THE COMPARATOR'S OWN read_F AND ITS CONTROLS ----
    fpath, _ = _self_build_F(tmp, "ok")
    rf = _try(lambda: G.read_F(fpath))
    unit("U31 comparator read_F ACCEPTS the producer's components_requested and trivial_step",
         rf is not None and set(rf["table"]) == {(dv, i) for dv, i in COMPONENTS}
         and rf["ctrl"] is not None)
    unit("U32 every registered component carries ALL FOUR steps -- the three graded plus the "
         "section-4 trivial baseline",
         rf is not None and all(set(rf["table"][(dv, i)]["fd"]) == set(STEPS["twist"]) | {TRIVIAL_STEP}
                                for dv, i in COMPONENTS))
    fdrop, _ = _self_build_F(tmp, "drop", components=COMPONENTS[:-1])
    unit("U33 comparator read_F REFUSES a table missing a registered component",
         _raises(lambda: G.read_F(fdrop)))
    ftriv, _ = _self_build_F(tmp, "triv", trivial=1.1e-3)
    unit("U34 comparator read_F REFUSES a trivial_step that is not 1.0e-3",
         _raises(lambda: G.read_F(ftriv)))
    _want_ctrl = PLANT / (2.0 * CTRL_STEP)
    unit("U35 comparator ctrl_control RECOVERS the producer's planted CTRL row (zero exactly 0.0, "
         "plant to 1e-9)",
         _try(lambda: abs(G.ctrl_control(rf)["instrument_ctrl_planted"] - _want_ctrl)
              <= 1e-12 * _want_ctrl, False) is True)
    unit("U36 comparator grader_plant_control sees its OWN plant added to every physical dCD",
         _try(lambda: G.grader_plant_control(tmp, fpath, "selftest")["grader_plant_seen"]) is True)

    # ---- H. THE GRADED READING OF THE PRODUCER'S OWN TABLE --------------------------
    gc = _try(lambda: G.grade_components(ra, rf, "CD"), {})
    unit("U37 comparator grade_components grades >= 3 components off the producer's table",
         gc.get("n_graded", 0) >= G.MIN_GRADED)
    unit("U38 the verdict it renders is in the FIXED vocabulary", gc.get("verdict") in G.VOCAB)
    unit("U39 no registered component is FLAGGED on the clean fixture (the three steps plateau)",
         gc.get("flagged_components_BY_NAME") == [])
    unit("U40 THE TRIVIAL BASELINE HITS ITS REGISTERED PREDICTION (> 15 %) -- the 1e-3 step is "
         "seen to FAIL, so the FD verdict is NOT withdrawn",
         gc.get("trivial_baseline", {}).get("prediction") == "HIT"
         and gc.get("trivial_baseline", {}).get("also_passed") is False)
    unit("U41 the sweep table carries a row for EVERY step including the trivial control",
         len(gc.get("sweep_table", [])) == len(STEPS["twist"]) + 1)
    gl = _try(lambda: G.grade_components(ra, rf, "CL"), {})
    unit("U42 the same holds for CL -- section 4.6 grades CD AND CL",
         gl.get("n_graded", 0) >= G.MIN_GRADED and gl.get("verdict") in G.VOCAB)
    fnotriv, _ = _self_build_F(tmp, "notriv", steps=STEPS["twist"])
    rnt = _try(lambda: G.read_F(fnotriv))
    unit("U43 the comparator's trivial baseline REFUSES a table that never evaluated 1e-3 -- "
         "which is why the producer MUST run the step that is meant to fail",
         _raises(lambda: G.grade_components(ra, rnt, "CD")))

    # ---- I. THE CTRL COLLISION GUARD, IN BOTH DIRECTIONS ----------------------------
    clean_rows = [fd_row(_self_probe, dv, i, fd_step_set()) for dv, i in COMPONENTS]
    ctrl = build_ctrl_row(SELF_CD0, SELF_CL0)
    unit("U44 check_ctrl_not_confusable passes on a clean table",
         _try(lambda: check_ctrl_not_confusable(clean_rows, ctrl)["collisions"]) == 0)
    zero_rows = [dict(r) for r in clean_rows]
    zero_rows[0] = json.loads(json.dumps(clean_rows[0]))
    zero_rows[0]["fd"][repr(STEPS["twist"][1])]["dCD"] = repr(0.0)
    unit("U45 check_ctrl_not_confusable REFUSES a MEASURED derivative that is exactly 0.0 "
         "(the CTRL zero-arm value)", _raises(lambda: check_ctrl_not_confusable(zero_rows, ctrl)))
    coll_rows = json.loads(json.dumps(clean_rows))
    coll_rows[0]["fd"][repr(STEPS["twist"][1])]["dCD"] = repr(PLANT / (2.0 * CTRL_STEP))
    unit("U46 check_ctrl_not_confusable REFUSES a MEASURED derivative equal to the CTRL planted "
         "constant", _raises(lambda: check_ctrl_not_confusable(coll_rows, ctrl)))
    unit("U47 the CTRL namespace is disjoint from the design variables",
         CTRL_NAME not in DVS and all(dv != CTRL_NAME for dv, _ in COMPONENTS))

    # ---- J. THE WRITTEN-ARTEFACT READ-BACK -----------------------------------------
    unit("U48 verify_written_F recovers the control from the file that will actually be graded",
         _try(lambda: verify_written_F(fpath)["ctrl_zero"]) == 0.0)
    unit("U49 verify_written_F REFUSES an artefact missing the trivial step for a component",
         _raises(lambda: verify_written_F(fnotriv)))
    unit("U50 verify_written_F REFUSES an adjoint_source md5 that is not an md5",
         _raises(lambda: verify_written_F(_self_build_F(
             tmp, "nosrc", wreck=lambda r: r["adjoint_source"].__setitem__("md5", "PLACEHOLDER"))[0])))
    unit("U51 verify_written_F REFUSES an artefact whose CTRL row was removed",
         _raises(lambda: verify_written_F(_self_build_F(
             tmp, "noctrl", wreck=lambda r: r.__setitem__(
                 "rows", [x for x in r["rows"] if x.get("dv") != CTRL_NAME]))[0])))
    unit("U52 verify_written_A REFUSES an A artefact whose twist array is too short for the "
         "registered components",
         _raises(lambda: verify_written_A(
             (lambda p: (write_json_fsync(p, build_A_record(
                 FD_LEVEL, 4, _self_ident(), "0" * 32, SELF_CD0, SELF_CL0,
                 {of: {"twist": [_num(v) for v in A_TWIST[:3]], "patchV": [_num(v) for v in A_PATCHV]}
                  for of in ("CD", "CL")}, {})), p)[1])(os.path.join(tmp, "A_short.json")), FD_LEVEL)))

    # ---- K. L-332 -------------------------------------------------------------------
    import ast as _ast
    unit("U53 ast.Assert census of this module is ZERO (L-332: a gate on `assert` gates on "
         "nothing under -O)",
         sum(1 for x in _ast.walk(_ast.parse(open(__file__).read())) if isinstance(x, _ast.Assert)) == 0)
    unit("U54 the suite ran the frozen unit count", n + 1 == EXPECTED_UNITS)

    print("\nD8G PRODUCER SELFTEST units=%d fails=%d" % (n, len(fails)))
    if fails:
        for f in fails:
            print("  FAILED UNIT: %s" % f)
        return 2
    return 0


def _selftest_main(argv):
    tmp = None
    for i, a in enumerate(argv):
        if a == "--tmpdir" and i + 1 < len(argv):
            tmp = argv[i + 1]
    if tmp is None:
        import tempfile
        tmp = tempfile.mkdtemp(prefix="d8g_of_selftest_")
    tmp = os.path.join(tmp, "of_%d" % int(time.time() * 1e6))
    os.makedirs(tmp, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    for i, a in enumerate(argv):
        if a == "--specdir" and i + 1 < len(argv):
            here = argv[i + 1]
    return selftest(tmp, here)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest_main(sys.argv))
    try:
        sys.exit(main(sys.argv))
    except Refusal as _exc:
        sys.stderr.write("D8G_OF REFUSE %s\n" % _exc)
        sys.exit(2)
