#!/usr/bin/env python3
"""
T26 COMPARATOR -- the motor-in-duct 3D rung, graded under CLAUDE.md rule 5.

REGISTERED PATH.  T26_PREREGISTRATION.md:805 registers this comparator at
`docs/campaigns/T-family/analyse_t26.py`.  It is written HERE and nowhere else,
because T26_PREREGISTRATION.md:106 makes the ABSENCE of
`verification/runs/T-family/T26_runs/` the rule-2 pre-compute condition of the
whole document: creating that directory -- even only to hold a script -- would
falsify the condition the freeze rests on.  The run root is created by
`launch_t26.sh` at launch and not one moment earlier.

WHAT IT GRADES (T26_PREREGISTRATION.md:557-566):
  Q1  T_max   = max(T) over `housing` u `core`,        from <endTime>/{housing,core}/T
  Q2  T_iface = area-average of T on the housing side  from <endTime>/housing/T boundaryField
  Q3  Q_strut = heat rate housing -> duct through the three struts, W

THE ORDER OF EVALUATION IS CLAUDE.md RULE 5, VERBATIM, AND IS `verdict_t26()`:
  (1) any level not iteratively converged (G-CONV) or not plateaued (G-ITER)
                                                         -> NOT A RESULT
  (2) the triple DIVERGENT, STAGNANT, OSCILLATORY or EXACT
                                                         -> NOT A RESULT, with
      the value, BOTH triples and BOTH orders printed beside it
  (3) CONVERGING -> PASS inside the pre-registered band, else GATE FAIL, GCI
      printed at Fs = 1.25.
  THE GATE CAN ONLY TURN A PASS OR GATE FAIL *INTO* NOT A RESULT, NEVER THE
  REVERSE -- proved by `--selftest`, which drives a NOT A RESULT triple whose
  value lies INSIDE the band and shows it does not become a PASS.
  A GCI IS NEVER QUOTED WHEN THE THREE VALUES ARE NOT MONOTONE: `gci()` returns
  no `GCI_pct` key at all in the OSCILLATORY, EXACT, DIVERGENT and STAGNANT
  states, so there is no number for a caller to print by mistake.

THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3; T26_PREREGISTRATION.md:769-782).
Every reader below can return a zero, and a broken reader returns the same
zero.  Each therefore plants a KNOWN perturbation, WRITES IT TO DISK, reads it
BACK FROM DISK through the SAME production function, and REFUSES if the reader
cannot see it.  The negative arm -- plant removed, the check must fire -- is
driven too, because a control that only ever passes proves nothing.

EXIT CODES, and the two refusal codes are deliberate, not a slip:
  0  every graded row PASS or NOT A RESULT, no GATE FAIL
  1  at least one GATE FAIL (a reportable graded outcome)
  2  REFUSAL -- a structural precondition failed (missing DONE marker, missing
     field, unreadable case).  CLAUDE.md rule 4: comparators refuse rather than
     degrade.
  3  REFUSAL -- THE COMPARATOR'S OWN PLANTED CONTROL FAILED, so nothing it
     printed is evidence.  T26_PREREGISTRATION.md:769-771 registers exit 3 for
     exactly this arm, and geometry_gate_t26.py (:238-240 of the registration)
     already uses 3 with the same meaning.  Both are refusals; neither degrades.

NO `assert` STATEMENT IN THIS FILE (L-332): `python3 -O` strips them, and a
control that vanishes under -O is not a control.  --selftest checks its own
AST for this and drives a planted assert through the same counter.

WHAT THIS COMPARATOR CANNOT SEE, named rather than hidden:
  * absolute accuracy of Q1/Q2/Q3.  T26_PREREGISTRATION.md:606-613 registers
    reference tier NONE for all three.  This is VERIFICATION, NOT VALIDATION.
  * the 3.75-degree azimuthal faceting of the source STL, which no mesh
    refinement can resolve (registration section 11 item 5).
  * whether the steady solver is grading a state the physics votes unsteady.

Usage:  python3 analyse_t26.py [--root DIR] [--json OUT]
        python3 analyse_t26.py --selftest
"""
import json
import math
import os
import re
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# --- FROZEN CONSTANTS, every one traced to a line of T26_PREREGISTRATION.md ---
R_REFINE = 1.5          # :424  h ratio = N^(1/3) = 1.500 at both steps
FS = 1.25               # :570  Roache factor of safety
PLANT_T = 1.234e-03     # K   :772, the T3 family value (analyse_t3.py:81)
PLANT_FLUX = 7.531e+00  # W   a known non-zero for the wallHeatFlux reader
PLANT_PHI = 2.468e-03   # kg/s a known non-zero for the phi reader
PLANT_RESID = 3.210e-07 # -    a known non-zero for the residual reader
PLANT_YPLUS = 4.321e+00 # -    a known non-zero for the y+ reader

LEVELS = ("L1", "L2", "L3")
END_TIME = {"L1": 8000, "L2": 12000, "L3": 16000}        # :544
CELLS_PROJECTED = {"L1": 885508, "L2": 2988590, "L3": 10086491}   # :430

# gates, T26_PREREGISTRATION.md:513-519
G_CONV = {"h": 1.0e-06, "p_rgh": 1.0e-05, "Ux": 1.0e-05, "Uy": 1.0e-05,
          "Uz": 1.0e-05, "k": 1.0e-05, "omega": 1.0e-05}
G_CONT = 1.0e-05        # :517  |sum(phi)| / |phi_in|
G_BAL = 1.0e-03         # :518  |sum(Q_wall) - P_loss| / P_loss
G_ITER_FACTOR = 0.1     # :519  iterative error <= 0.1 x level-to-level difference
P_BAND = (0.5, 2.5)     # :581  observed order band; outside ADDS A LEVEL
P_LOSS_W = 305.0        # :383  registered operating point

FLUID_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")
SOLID_REGIONS = ("core", "housing", "duct")

EXIT_OK, EXIT_FAIL, EXIT_REFUSE, EXIT_BLIND = 0, 1, 2, 3


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def refuse_blind(msg):
    """The planted control failed.  Nothing this comparator printed is evidence."""
    print("REFUSE (PLANTED CONTROL FAILED, exit 3): " + msg)
    print("        A zero from a reader not shown able to see a non-zero is not")
    print("        evidence (CLAUDE.md rule 3).  No verdict is issued.")
    sys.exit(EXIT_BLIND)


# ===========================================================================
# OpenFOAM field readers.  EVERY ONE OF THESE CAN RETURN A ZERO, so every one
# of them is planted into below.
# ===========================================================================
def _field_lines(path):
    if not os.path.isfile(path):
        refuse("no field file %s" % path)
    with open(path, errors="replace") as fh:
        return fh.read().split("\n")


def read_internal_scalars(path):
    """Return (values, kind, first_value_line_index).

    Handles `internalField uniform X;` and `internalField nonuniform
    List<scalar> N ( v v v ... );`.  The line index is returned so the plant can
    be located STRUCTURALLY, by position, NEVER by matching a value -- a plant
    located by value cannot be distinguished from a value that was already
    there (analyse_t3.py:287, the same discipline)."""
    lines = _field_lines(path)
    for i, ln in enumerate(lines):
        m = re.match(r"\s*internalField\s+uniform\s+([-0-9.eE+]+)\s*;", ln)
        if m:
            return [float(m.group(1))], "uniform", i
        if re.match(r"\s*internalField\s+nonuniform", ln):
            for j in range(i, min(i + 6, len(lines) - 2)):
                if lines[j].strip().isdigit() and lines[j + 1].strip() == "(":
                    n = int(lines[j].strip())
                    vals, k = [], j + 2
                    while k < len(lines) and len(vals) < n:
                        s = lines[k].strip()
                        if s == ")":
                            break
                        try:
                            vals.append(float(s))
                        except ValueError:
                            pass
                        k += 1
                    return vals, "nonuniform", j + 2
    refuse("cannot locate an internalField in %s" % path)


def read_boundary_scalars(path, patch_substr):
    """Area-UNWEIGHTED mean over every boundary patch whose name contains
    `patch_substr`.  Returns (mean, n_values, first_value_line_index).

    The unweighted mean is a REGISTERED LIMITATION and is stated as one: the
    exact area weights live in the polyMesh, which this reader does not open.
    T26_PREREGISTRATION.md:562 registers Q2 as an area average; this reader
    computes the face-count average and REPORTS the difference class rather
    than pretending they are the same.  On a boundary of nearly uniform face
    area the two agree; on this geometry they do not exactly, and the gap is
    named in the output line for Q2, never absorbed."""
    lines = _field_lines(path)
    vals, first_idx = [], None
    in_patch = False
    for i, ln in enumerate(lines):
        if patch_substr in ln and re.match(r"\s*\S*%s\S*\s*$" % re.escape(patch_substr), ln):
            in_patch = True
            continue
        if in_patch:
            m = re.match(r"\s*value\s+uniform\s+([-0-9.eE+]+)\s*;", ln)
            if m:
                vals.append(float(m.group(1)))
                first_idx = i if first_idx is None else first_idx
                in_patch = False
                continue
            if re.match(r"\s*value\s+nonuniform", ln):
                for j in range(i, min(i + 6, len(lines) - 2)):
                    if lines[j].strip().isdigit() and lines[j + 1].strip() == "(":
                        n = int(lines[j].strip())
                        k = j + 2
                        first_idx = k if first_idx is None else first_idx
                        while k < len(lines) and n > 0:
                            s = lines[k].strip()
                            if s == ")":
                                break
                            try:
                                vals.append(float(s))
                                n -= 1
                            except ValueError:
                                pass
                            k += 1
                        break
                in_patch = False
                continue
            if ln.strip() == "}":
                in_patch = False
    if not vals:
        return None, 0, None
    return sum(vals) / len(vals), len(vals), first_idx


def read_q1_tmax(case, endtime):
    """Q1: max(T) over housing u core, from the internalField of both."""
    vals = []
    for reg in ("housing", "core"):
        p = os.path.join(case, "%g" % endtime, reg, "T")
        v, _kind, _idx = read_internal_scalars(p)
        vals.extend(v)
    if not vals:
        refuse("Q1 read no T values at endTime %g in %s" % (endtime, case))
    return max(vals)


def read_q2_tiface(case, endtime):
    """Q2: mean T on the housing side of the fluid/housing interface."""
    p = os.path.join(case, "%g" % endtime, "housing", "T")
    v, n, _idx = read_boundary_scalars(p, "fluid")
    if v is None:
        refuse("Q2 found no housing-side interface patch in %s" % p)
    return v, n


def resolve_unique(pattern):
    """Resolve a glob that MUST match exactly one file.  Returns (path, why).
    `path` is None and `why` is set when it matches zero or MORE THAN ONE.

    THE COLLISION THIS REFUSES.  OpenFOAM does not overwrite a function-object
    file on restart -- it writes a SECOND one beside the first, so a restarted
    case holds `wallHeatFlux.dat` AND `wallHeatFlux_0.dat`, and both match the
    glob a grader reads.  Whichever the filesystem happens to return first then
    supplies the number.  That is a WRONG NUMBER, not a crash, and nothing in
    the run fails to announce it.  Reported by cfd 2026-09-10 against a restart
    collision on `moment.dat` / `moment_0.dat`.

    `mark_done_t26.py`'s clause 7 already REFUSES a case with a non-empty
    `postProcessing/`, so this should be unreachable in a clean run.  It is
    here anyway because A GUARD AND A READER THAT BOTH CHECK is the pattern
    that saved K2bU3R3: its launch guard was live and enforcing even though the
    rest of that instrument could not execute at all.  One of the two being
    dead must not be enough to produce a number."""
    import glob as _glob
    hits = sorted(_glob.glob(pattern))
    if not hits:
        return None, "no file matches %s" % pattern
    if len(hits) > 1:
        return None, ("%d files match %s -- %s. OpenFOAM writes a SECOND "
                      "function-object file on restart rather than overwriting, "
                      "so this glob cannot say which run produced which number. "
                      "REFUSED rather than picking one."
                      % (len(hits), pattern, ", ".join(os.path.basename(h) for h in hits)))
    return hits[0], None


def read_wall_heat_flux(path, key_substr):
    """Q3 / G-BAL: sum the flux column of a wallHeatFlux function-object file
    over every row whose patch name contains `key_substr`.

    THE DEFECT THIS SIGNATURE EXISTS FOR: `dict.get(key, 0.0)` cannot tell an
    ABSENT key from a MEASURED ZERO -- the same defect scripts/cost_channel.py
    was written for, where a ledger recorded 0.00 core-min for a run that cost
    34.23.  This returns (total, n_rows); n_rows == 0 is ABSENT and is NEVER
    reported as a measured zero."""
    if not path or not os.path.isfile(path):
        return None, 0
    total, n = 0.0, 0
    with open(path, errors="replace") as fh:
        for ln in fh:
            if ln.lstrip().startswith("#"):
                continue
            parts = ln.split()
            if len(parts) < 2:
                continue
            if key_substr and key_substr not in ln:
                continue
            try:
                total += float(parts[-1])
                n += 1
            except ValueError:
                continue
    return (total, n) if n else (None, 0)


def read_phi_sum(case, endtime):
    """G-CONT: (sum of all phi faces, count).  Absent is not zero."""
    p = os.path.join(case, "%g" % endtime, "fluid", "phi")
    if not os.path.isfile(p):
        return None, 0
    v, _kind, _idx = read_internal_scalars(p)
    return (sum(v), len(v)) if v else (None, 0)


def read_residuals(logpath):
    """G-CONV: the LAST initial residual per field from log.solve.
    Returns {field: value}; a field never seen is ABSENT, not zero."""
    if not os.path.isfile(logpath):
        return {}
    pat = re.compile(r"Solving for (\S+),\s*Initial residual = ([0-9.eE+-]+)")
    out = {}
    with open(logpath, errors="replace") as fh:
        for ln in fh:
            m = pat.search(ln)
            if m:
                out[m.group(1)] = float(m.group(2))
    return out


def strip_foam_comments(text):
    """Remove `//` line comments and `/* */` block comments BEFORE any reader
    matches.  A COMMENTED-OUT line is not the live mesh: on 2026-09-10 the
    closure team read a commented-out `blockMeshDict` line as the live setting
    and certified three families as 3D that were one cell thick.  Every reader
    in this file that touches a dictionary or a log passes through here first."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def read_geometric_directions(logpath):
    """D-3D: the ONLY artifact that can establish dimensionality -- checkMesh's
    own line on a BUILT mesh.  Returns (n, verbatim_line); ABSENT is (None, None)
    and is NEVER reported as a passing 3.

    WHY THIS READER EXISTS, and it is a hazard this rung was handed rather than
    one it invented.  On 2026-09-10 the closure team offered three "genuinely
    3D" families and ALL THREE turned out ONE CELL THICK with `empty` spanwise
    patches: the board carried correct cell counts and INFERRED dimensionality
    that nothing had checked, and a COMMENTED-OUT blockMeshDict line was read as
    the live mesh.  The heat-transfer supervisor then ran the same check on
    T4e -- the rung CASE_PROTOCOL section 7 names as this team's FRONT -- and
    every level read `Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)`
    with 1 `empty` and 2 `wedge` patches.  T4e IS NOT 3D.

    T26's entire justification is that it is the GENUINELY 3D motor-in-duct
    rung.  Until this reader returns 3 on a built mesh, that claim rests on a
    GEOMETRY GATE -- a description of an INTENDED shape -- and a geometry gate
    CANNOT establish dimensionality.  Neither can blockMeshDict or
    snappyHexMeshDict: those are the artifacts that misled closure, and this
    reader deliberately refuses to look at them."""
    if not os.path.isfile(logpath):
        return None, None
    pat = re.compile(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions")
    with open(logpath, errors="replace") as fh:
        for ln in fh:
            live = strip_foam_comments(ln)
            m = pat.search(live)
            if m:
                return int(m.group(1)), live.rstrip("\n").strip()
    return None, None


def read_checkmesh_provenance(logpath):
    """G-PROV: which check set produced this log?  Returns (cmdline, has_geo,
    has_topo) or (None, False, False) if no command line was recorded.

    READ RAW, DELIBERATELY -- this is the ONE reader that does NOT pass through
    strip_foam_comments().  The provenance line is metadata ABOUT the artifact,
    not mesh data inside it, and stripping comments from it would let a
    `//`-prefixed command line vanish from the very reader that must check it.
    (That interaction was created and caught in the same session, before the
    freeze; the launcher now also writes the line unprefixed, so the two
    defences are independent.)

    WHY THIS GATE EXISTS.  Bare `checkMesh` prints `Mesh OK.` on a mesh that
    FAILS checks which only run under -allGeometry and -allTopology.  MEASURED
    on T26's own probe mesh, 2026-09-10, same mesh and same binary:
        checkMesh                           -> "Mesh OK."
        checkMesh -allGeometry -allTopology -> "Failed 2 mesh checks."
                                               2,320 small-determinant cells
                                              13,099 concave cells
    cfd spent three M6CP1 smoke rungs on a mesh its stage-2 gate could never
    have refused.  A directions line read out of a weaker log is a fact about
    a check set nobody ran."""
    if not os.path.isfile(logpath):
        return None, False, False
    with open(logpath, errors="replace") as fh:
        for ln in fh:
            if "CHECKMESH COMMAND LINE:" in ln:
                cmd = ln.split("CHECKMESH COMMAND LINE:", 1)[1].strip()
                return cmd, ("-allGeometry" in cmd), ("-allTopology" in cmd)
            if ln.startswith("Create mesh") or ln.startswith("Time ="):
                break          # past the header; no provenance line was written
    return None, False, False


def read_min_cell_dimension(logpath):
    """G-MINCELL: the smallest cell dimension in the mesh, as
    min(cell volume)**(1/3), from checkMesh's own `Min volume` line.
    Returns (dim_m, min_vol) or (None, None).  ABSENT is never a passing value.

    A cusped trailing edge PASSES BOTH CHECK SETS and still destroyed the M6.
    T26's three struts have sharp, unfilleted trailing edges (registration
    section 11 item 4) -- exactly that geometry."""
    if not os.path.isfile(logpath):
        return None, None
    v = None
    pat = re.compile(r"Min volume\s*=\s*([0-9.eE+-]+)")
    with open(logpath, errors="replace") as fh:
        for ln in fh:
            m = pat.search(strip_foam_comments(ln))
            if m:
                # checkMesh ends the sentence with a FULL STOP: the real line is
                #     "Min volume = 1.10863e-09."
                # and the character class above swallows that trailing period, so
                # float() raises.  MEASURED against a real probe log, 2026-09-10 --
                # the synthetic fixture had no trailing period and never saw it.
                # Strip trailing periods, and FAIL CLOSED (None) on anything still
                # unparseable rather than letting an exception escape a reader whose
                # whole job is to refuse.
                tok = m.group(1).rstrip(".")
                try:
                    v = float(tok)
                except ValueError:
                    return None, None
    if v is None or v <= 0:
        return None, v
    return v ** (1.0 / 3.0), v


# G-MINCELL floor, REGISTERED as a FRACTION so it scales with the level rather
# than being re-chosen per level (registration amendment 13.7).
MIN_CELL_FRACTION = 0.10
# smallest registered surface cell per level, metres (registration :417-419,
# strut surface level 3, shifted one rung by amendment 13.3)
SMALLEST_SURFACE_CELL = {"L1": 1.500e-03, "L2": 1.000e-03, "L3": 0.667e-03}


def mincell_verdict(level, dim_m):
    floor = MIN_CELL_FRACTION * SMALLEST_SURFACE_CELL[level]
    if dim_m is None:
        return dict(ok=False, verdict="NOT A RESULT", floor_m=floor, dim_m=None,
                    why="checkMesh recorded no usable `Min volume`, so the minimum "
                        "cell dimension is UNMEASURED. Unmeasured is not passing.")
    if dim_m < floor:
        return dict(ok=False, verdict="NOT A RESULT", floor_m=floor, dim_m=dim_m,
                    why="minimum cell dimension %.4g m is BELOW the registered floor "
                        "%.4g m (%.2f x the level's smallest surface cell %.4g m). A "
                        "cell an order of magnitude below the intended surface "
                        "resolution is a snap artifact, not a resolved feature -- and "
                        "a cusped trailing edge passes every checkMesh set and still "
                        "destroyed the M6."
                        % (dim_m, floor, MIN_CELL_FRACTION, SMALLEST_SURFACE_CELL[level]))
    return dict(ok=True, verdict="G-MINCELL PASS", floor_m=floor, dim_m=dim_m,
                why="minimum cell dimension %.4g m >= floor %.4g m" % (dim_m, floor))


def read_checkmesh_failures(logpath):
    """G-MESHQ: what did `checkMesh` itself FAIL?  Returns (n_failed, [lines])
    or (None, []) when the log carries no verdict line at all.

    THE GAP THIS CLOSES, found by reading my own comparator after it had already
    been committed: D-3D checked DIRECTIONS, PATCH TYPES and PROVENANCE, and
    G-MINCELL checked the SMALLEST CELL -- and NOTHING read checkMesh's own
    `Failed N mesh checks` verdict.  The comparator would have graded, with a
    clean 3D CONFIRMED, a mesh whose own quality tool had failed it.  Measured
    on T26's first probe: 2,320 small-determinant cells and 13,099 concave
    cells, under a `Mesh has 3 geometric directions` line that read perfectly.

    `Mesh OK.` is NOT accepted as a pass on its own -- it is exactly what bare
    `checkMesh` prints on a mesh the full check set fails, and G-PROV is what
    establishes the log came from the full set.  The two gates are independent
    and both must hold."""
    if not os.path.isfile(logpath):
        return None, []
    n, lines, saw_ok = None, [], False
    with open(logpath, errors="replace") as fh:
        for ln in fh:
            t = strip_foam_comments(ln).rstrip()
            if t.lstrip().startswith("***"):
                lines.append(t.strip())
            m = re.search(r"Failed (\d+) mesh check", t)
            if m:
                n = int(m.group(1))
            if t.strip() == "Mesh OK.":
                saw_ok = True
    if n is None and saw_ok:
        n = 0
    return n, lines


# G-MESHQ TOLERANCE, REGISTERED.  Default ZERO: any check `checkMesh
# -allGeometry -allTopology` fails is a refusal.  A named, justified tolerance
# may be added here BEFORE the freeze while the rule-2 window is open -- as a
# PRE-REGISTERED THRESHOLD, never as a thing noticed afterwards and accepted.
# Each entry is check-name -> (max cells, written justification).
MESHQ_TOLERANCE = {}


def meshq_verdict(n_failed, lines):
    if n_failed is None:
        return dict(ok=False, verdict="NOT A RESULT", n_failed=None, lines=lines,
                    why="log.checkMesh carries NO verdict line -- neither `Mesh OK.` "
                        "nor `Failed N mesh checks`. Mesh quality is UNMEASURED, and "
                        "unmeasured is not passing.")
    if n_failed == 0:
        return dict(ok=True, verdict="G-MESHQ PASS", n_failed=0, lines=lines,
                    why="checkMesh -allGeometry -allTopology failed no checks")
    untolerated = []
    for ln in lines:
        hit = next((k for k in MESHQ_TOLERANCE if k.lower() in ln.lower()), None)
        if hit is None:
            untolerated.append(ln)
            continue
        cap, _why = MESHQ_TOLERANCE[hit]
        m = re.search(r"number of cells:\s*(\d+)", ln)
        if m is None or int(m.group(1)) > cap:
            untolerated.append(ln)
    if untolerated:
        return dict(ok=False, verdict="NOT A RESULT", n_failed=n_failed,
                    lines=lines, untolerated=untolerated,
                    why="checkMesh -allGeometry -allTopology FAILED %d check(s) with "
                        "no registered tolerance covering: %s. The mesh is fixed, or "
                        "a tolerance is registered with its justification BEFORE the "
                        "freeze -- the gate is never relaxed to let a mesh through."
                        % (n_failed, "; ".join(untolerated)))
    return dict(ok=True, verdict="G-MESHQ PASS (within registered tolerance)",
                n_failed=n_failed, lines=lines,
                why="every failed check is covered by a PRE-REGISTERED tolerance in "
                    "MESHQ_TOLERANCE, each with its written justification")


def read_patch_type_census(boundary_path):
    """D-3D: a census of patch types from constant/polyMesh/boundary, the BUILT
    mesh's own boundary file.  Returns (dict type -> count, total) or (None, 0).

    ANY `empty` OR `wedge` PATCH IS DISQUALIFYING FOR A 3D CLAIM.  An absent
    boundary file returns None, never an empty census that would read as
    'no empty patches found'."""
    if not os.path.isfile(boundary_path):
        return None, 0
    txt = strip_foam_comments(open(boundary_path, errors="replace").read())
    census = {}
    # NOT anchored to line start: a real boundary file puts `type` on its own
    # line, but an inline `{ type empty; }` is the same declaration and a
    # census that missed it would under-count exactly the patch class that
    # disqualifies a 3D claim.  Comments are stripped FIRST.
    for m in re.finditer(r"\btype\s+([A-Za-z]+)\s*;", txt):
        census[m.group(1)] = census.get(m.group(1), 0) + 1
    return (census, sum(census.values())) if census else (None, 0)


def dimensionality_verdict(ndirs, verbatim, census, provenance=None):
    """The D-3D gate.  Returns dict(ok, verdict, why, evidence).

    NOT A RESULT is the ONLY outcome available when the mesh is not shown to be
    3D: the rung's registered premise (registration :24-44, `T26 is the
    genuinely three-dimensional successor`) fails, and a verification verdict
    on a premise that failed is not a verdict."""
    ev = dict(geometric_directions=ndirs, checkMesh_line=verbatim,
              patch_type_census=census, checkMesh_provenance=provenance)
    # G-PROV FIRST: a directions line read out of a log that never ran the full
    # check set is a fact about a check set nobody ran.
    if provenance is not None:
        cmd, has_geo, has_topo = provenance
        if cmd is None:
            return dict(ok=False, verdict="NOT A RESULT", evidence=ev,
                        why="log.checkMesh records NO command line, so which check "
                            "set produced it is UNKNOWABLE. The artifact must prove "
                            "which instrument produced it.")
        if not (has_geo and has_topo):
            missing = " ".join(f for f, p in (("-allGeometry", has_geo),
                                              ("-allTopology", has_topo)) if not p)
            return dict(ok=False, verdict="NOT A RESULT", evidence=ev,
                        why="log.checkMesh was produced WITHOUT %s (recorded command "
                            "line: %r). Bare checkMesh prints `Mesh OK.` on a mesh "
                            "that fails those checks -- MEASURED on T26's own probe "
                            "mesh: bare said `Mesh OK.`, the full set said `Failed 2 "
                            "mesh checks` with 2,320 small-determinant and 13,099 "
                            "concave cells. This log is not graded." % (missing, cmd))
    if ndirs is None:
        return dict(ok=False, verdict="NOT A RESULT", evidence=ev,
                    why="checkMesh's `Mesh has N geometric (non-empty/wedge) "
                        "directions` line was NOT FOUND. Dimensionality is "
                        "UNMEASURED, and unmeasured is not 3. It is never "
                        "certified from the geometry gate, blockMeshDict or "
                        "snappyHexMeshDict -- those are the artifacts that "
                        "misled the closure team on 2026-09-10.")
    if ndirs != 3:
        return dict(ok=False, verdict="NOT A RESULT", evidence=ev,
                    why="MEASURED %d geometric directions, not 3. THE RUNG'S "
                        "PREMISE FAILS: T26 exists to be the genuinely 3D "
                        "successor to the 5-degree T23/T24 wedge, and a mesh "
                        "with %d geometric directions is not that. Verbatim: %r"
                        % (ndirs, ndirs, verbatim))
    if census is None:
        return dict(ok=False, verdict="NOT A RESULT", evidence=ev,
                    why="constant/polyMesh/boundary was not readable, so the "
                        "empty/wedge patch census is UNMEASURED. checkMesh read "
                        "3 directions, but the census is a SECOND, independent "
                        "witness and an absent one is not a clean one.")
    bad = {k: v for k, v in census.items() if k in ("empty", "wedge")}
    if bad:
        return dict(ok=False, verdict="NOT A RESULT", evidence=ev,
                    why="checkMesh read 3 geometric directions BUT the boundary "
                        "carries %s -- disqualifying for a 3D claim. The two "
                        "witnesses disagree and the disagreement is itself the "
                        "finding." % ", ".join("%d %s patch(es)" % (v, k)
                                               for k, v in sorted(bad.items())))
    return dict(ok=True, verdict="3D CONFIRMED", evidence=ev,
                why="checkMesh: %r; boundary census carries no empty and no "
                    "wedge patch. Two independent witnesses on the BUILT mesh."
                    % verbatim)


def read_yplus(logpath):
    """REPORTED, NOT GATED (registration :617-620, lesson C-209: T5b gated y+ at
    2.00, measured 2.31, and every one of its six graded rows became NOT A
    RESULT on a statistic).  Returns (max, n_rows); absent is not zero."""
    if not os.path.isfile(logpath):
        return None, 0
    vals = []
    pat = re.compile(r"max:\s*([0-9.eE+-]+)")
    with open(logpath, errors="replace") as fh:
        for ln in fh:
            if "y+" in ln or "yPlus" in ln:
                m = pat.search(ln)
                if m:
                    vals.append(float(m.group(1)))
    return (max(vals), len(vals)) if vals else (None, 0)


# ===========================================================================
# PLANTED-ZERO CONTROLS -- six readers, each driven in BOTH directions.
# Each plants ON DISK, reads back THROUGH THE PRODUCTION FUNCTION, and the
# negative arm removes the plant and requires the check to FIRE.
# ===========================================================================
def plant_into_scalar_field(path, plant):
    """Add `plant` to the FIRST internal value of an OpenFOAM scalar field, IN
    PLACE, then read the file BACK FROM DISK to prove the plant landed.
    Located STRUCTURALLY by line index, never by value (analyse_t3.py:287)."""
    _vals, kind, idx = read_internal_scalars(path)
    lines = _field_lines(path)
    if kind == "uniform":
        m = re.match(r"(\s*internalField\s+uniform\s+)([-0-9.eE+]+)(\s*;.*)", lines[idx])
        before = float(m.group(2))
        lines[idx] = "%s%r%s" % (m.group(1), before + plant, m.group(3))
    else:
        before = float(lines[idx].strip())
        lines[idx] = repr(before + plant)
    with open(path, "w") as fh:
        fh.write("\n".join(lines))
    back_vals, _k, _i = read_internal_scalars(path)          # FROM DISK
    after = back_vals[0]
    if abs((after - before) - plant) > 1e-12:
        raise RuntimeError("the plant did not land in %s: %r -> %r" % (path, before, after))
    return before, after


def _forge_scalar_field(path, values, uniform=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n version 2.0;\n class volScalarField;\n}\n")
        if uniform:
            fh.write("internalField   uniform %r;\n" % values[0])
        else:
            fh.write("internalField   nonuniform List<scalar>\n%d\n(\n" % len(values))
            fh.write("\n".join(repr(v) for v in values))
            fh.write("\n)\n;\n")
        fh.write("boundaryField\n{\n    housing_to_fluid\n    {\n"
                 "        type            fixedValue;\n"
                 "        value           uniform %r;\n    }\n}\n" % values[0])


def control_T_reader(verbose=True):
    """Q1/Q2 reader.  POSITIVE: plant PLANT_T, the reader's max must rise by it.
    NEGATIVE: no plant, the check must NOT fire."""
    tmp = tempfile.mkdtemp(prefix="t26_plant_T_")
    try:
        base = [300.0, 301.0, 302.5]
        for uni in (False, True):
            p = os.path.join(tmp, "u" if uni else "n", "T")
            _forge_scalar_field(p, base, uniform=uni)
            v0, _k, _i = read_internal_scalars(p)
            m0 = max(v0)
            before, after = plant_into_scalar_field(p, PLANT_T)
            v1, _k, _i = read_internal_scalars(p)
            m1 = max(v1)
            seen = (m1 - m0) if uni else (v1[0] - v0[0])
            if abs(seen - PLANT_T) > 1e-12:
                return dict(passed=False, arm="positive/%s" % ("uniform" if uni else "nonuniform"),
                            planted=PLANT_T, seen=seen,
                            why="the T reader could not see a %g K plant it wrote to disk" % PLANT_T)
            # NEGATIVE ARM: rebuild clean, no plant, the difference must be 0
            _forge_scalar_field(p, base, uniform=uni)
            v2, _k, _i = read_internal_scalars(p)
            if abs((v2[0] - v0[0])) > 1e-15:
                return dict(passed=False, arm="negative/%s" % ("uniform" if uni else "nonuniform"),
                            why="the T reader reported a change with NO plant present")
        return dict(passed=True, planted=PLANT_T, read_back_delta=after - before,
                    arms="positive+negative on uniform and nonuniform")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_boundary_reader():
    """Q2's boundaryField path, planted and read back from disk."""
    tmp = tempfile.mkdtemp(prefix="t26_plant_B_")
    try:
        p = os.path.join(tmp, "T")
        _forge_scalar_field(p, [300.0, 301.0], uniform=False)
        m0, n0, _i = read_boundary_scalars(p, "fluid")
        if m0 is None:
            return dict(passed=False, why="the boundary reader saw no interface patch at all")
        txt = open(p).read().replace("value           uniform %r;" % 300.0,
                                     "value           uniform %r;" % (300.0 + PLANT_T))
        open(p, "w").write(txt)
        m1, n1, _i = read_boundary_scalars(p, "fluid")
        seen = m1 - m0
        if abs(seen - PLANT_T) > 1e-12:
            return dict(passed=False, planted=PLANT_T, seen=seen, n=n1,
                        why="the boundary reader could not see a %g K plant" % PLANT_T)
        # NEGATIVE ARM: a patch that does not match must NOT be counted
        blind, nb, _i = read_boundary_scalars(p, "no_such_patch_token")
        if blind is not None:
            return dict(passed=False, why="the boundary reader matched a patch that does not exist")
        return dict(passed=True, planted=PLANT_T, seen=seen, n_values=n1,
                    negative_arm="a non-matching patch returns None, NOT 0.0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_flux_reader():
    """Q3 / G-BAL.  The negative arm is the one that matters: an ABSENT file
    must return None, never 0.0 -- the cost_channel defect class."""
    tmp = tempfile.mkdtemp(prefix="t26_plant_Q_")
    try:
        p = os.path.join(tmp, "wallHeatFlux.dat")
        absent, na = read_wall_heat_flux(os.path.join(tmp, "not_there.dat"), "strut")
        if absent is not None or na != 0:
            return dict(passed=False, why="an ABSENT wallHeatFlux file returned %r, not None -- "
                                          "a reader that cannot tell absent from zero grades nothing" % absent)
        with open(p, "w") as fh:
            fh.write("# Time patch flux\n")
            fh.write("1 housing_to_duct_strutA %r\n" % PLANT_FLUX)
            fh.write("1 housing_to_duct_strutB %r\n" % PLANT_FLUX)
            fh.write("1 some_other_patch 999.0\n")
        tot, n = read_wall_heat_flux(p, "strut")
        if n != 2 or abs(tot - 2 * PLANT_FLUX) > 1e-9:
            return dict(passed=False, planted=2 * PLANT_FLUX, seen=tot, n=n,
                        why="the flux reader could not see its planted rows")
        # THE RESTART COLLISION: two files where one is expected -> REFUSE,
        # never pick one. A guard and a reader that both check.
        one, why1 = resolve_unique(os.path.join(tmp, "wallHeatFlux*.dat"))
        if one is None:
            return dict(passed=False, why="a single wallHeatFlux.dat did not resolve: %s" % why1)
        open(os.path.join(tmp, "wallHeatFlux_0.dat"), "w").write("# restart copy\n")
        two, why2 = resolve_unique(os.path.join(tmp, "wallHeatFlux*.dat"))
        if two is not None or "2 files match" not in (why2 or ""):
            return dict(passed=False, why="a restart COLLISION (wallHeatFlux.dat + "
                                          "wallHeatFlux_0.dat) was NOT refused: %r" % (why2,))
        os.remove(os.path.join(tmp, "wallHeatFlux_0.dat"))
        zero, why0 = resolve_unique(os.path.join(tmp, "no_such_glob*.dat"))
        if zero is not None or "no file matches" not in (why0 or ""):
            return dict(passed=False, why="an empty glob did not report as empty")
        # NEGATIVE ARM: a key that matches nothing is ABSENT, not zero
        none_tot, none_n = read_wall_heat_flux(p, "no_such_strut")
        if none_tot is not None or none_n != 0:
            return dict(passed=False, why="a non-matching key returned %r, not None" % none_tot)
        return dict(passed=True, planted=2 * PLANT_FLUX, seen=tot, n_rows=n,
                    negative_arm="absent file and non-matching key both return None, NOT 0.0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_phi_reader():
    """G-CONT.  Plant a known non-zero flux into phi and read the sum back."""
    tmp = tempfile.mkdtemp(prefix="t26_plant_phi_")
    try:
        case = os.path.join(tmp, "c")
        p = os.path.join(case, "10", "fluid", "phi")
        _forge_scalar_field(p, [0.0, 0.0, 0.0], uniform=False)
        s0, n0 = read_phi_sum(case, 10)
        if n0 == 0:
            return dict(passed=False, why="the phi reader saw no faces at all")
        plant_into_scalar_field(p, PLANT_PHI)
        s1, n1 = read_phi_sum(case, 10)
        if abs((s1 - s0) - PLANT_PHI) > 1e-12:
            return dict(passed=False, planted=PLANT_PHI, seen=s1 - s0,
                        why="the phi reader could not see its plant")
        # NEGATIVE ARM: absent phi is None, never 0.0
        miss, nm = read_phi_sum(case, 99)
        if miss is not None or nm != 0:
            return dict(passed=False, why="an absent phi returned %r, not None" % miss)
        return dict(passed=True, planted=PLANT_PHI, seen=s1 - s0, n_faces=n1,
                    negative_arm="an absent time directory returns None, NOT 0.0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_residual_reader():
    """G-CONV.  A synthetic residual line at a known value, read back."""
    tmp = tempfile.mkdtemp(prefix="t26_plant_r_")
    try:
        p = os.path.join(tmp, "log.solve")
        with open(p, "w") as fh:
            fh.write("Solving for h, Initial residual = 1.0, Final residual = 0.1\n")
            fh.write("Solving for h, Initial residual = %r, Final residual = 1e-12\n" % PLANT_RESID)
        r = read_residuals(p)
        if "h" not in r or abs(r["h"] - PLANT_RESID) > 1e-15:
            return dict(passed=False, planted=PLANT_RESID, seen=r.get("h"),
                        why="the residual reader could not see its planted line")
        # NEGATIVE ARM: a field never solved for is ABSENT, not zero
        if "p_rgh" in r:
            return dict(passed=False, why="the residual reader invented a p_rgh row")
        empty = read_residuals(os.path.join(tmp, "no_log"))
        if empty:
            return dict(passed=False, why="an absent log produced residuals")
        return dict(passed=True, planted=PLANT_RESID, seen=r["h"],
                    negative_arm="an unsolved field is ABSENT from the dict, NOT 0.0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_yplus_reader():
    tmp = tempfile.mkdtemp(prefix="t26_plant_y_")
    try:
        p = os.path.join(tmp, "log.yPlus")
        with open(p, "w") as fh:
            fh.write("patch hub y+ : min: 0.4 max: %r average: 0.9\n" % PLANT_YPLUS)
        v, n = read_yplus(p)
        if n == 0 or abs(v - PLANT_YPLUS) > 1e-12:
            return dict(passed=False, planted=PLANT_YPLUS, seen=v,
                        why="the y+ reader could not see its planted line")
        miss, nm = read_yplus(os.path.join(tmp, "no_such"))
        if miss is not None or nm != 0:
            return dict(passed=False, why="an absent y+ log returned %r, not None" % miss)
        return dict(passed=True, planted=PLANT_YPLUS, seen=v,
                    negative_arm="an absent log returns None, NOT 0.0")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_cost_reader():
    """MANDATORY (registration :780-782): scripts/cost_channel.py's own plant
    control, including its blind_production_reader negative arm.  The
    heat-transfer supervisor ruled 2026-09-10 that this is a FREEZE
    PRECONDITION, so its absence is a REFUSAL and never a skip."""
    sp = os.path.abspath(os.path.join(HERE, "..", "..", "..", "scripts"))
    cc = os.path.join(sp, "cost_channel.py")
    if not os.path.isfile(cc):
        return dict(passed=False, why="scripts/cost_channel.py is absent; the registration "
                                      "makes it a freeze precondition, so this is a refusal")
    # UPSTREAM DEFECT, MEASURED 2026-09-10 AND NOT REPAIRED FROM HERE.
    # scripts/cost_channel.py:141 computes REPO as dirname(__file__)/../../..
    # Its own usage docstring (:4-6) shows it was written to live at
    # `verification/runs/T-family/cost_channel.py`, from which three `..` DO
    # reach the repo root.  It has since been moved to `scripts/`, from which
    # three `..` reach `/home`, so every fixture path it builds is wrong and
    # `assert_cost_channel_armed()` raises SystemExit for EVERY caller on this
    # box.  The direction is fail-closed -- it refuses rather than reporting a
    # false cost -- but the channel the heat-transfer supervisor made a T26
    # FREEZE PRECONDITION on 2026-09-10 is currently unusable by anyone.
    # This comparator DIAGNOSES it and REFUSES; it does not patch a shared
    # script in another team's territory.  Routed to the supervisor.
    if sp not in sys.path:
        sys.path.insert(0, sp)
    try:
        import cost_channel                                   # noqa: E402
    except Exception as e:                                    # pragma: no cover
        return dict(passed=False, why="cost_channel.py did not import: %r" % (e,))
    tmp = tempfile.mkdtemp(prefix="t26_cost_")
    try:
        armed = cost_channel.assert_cost_channel_armed(tmp)
        return dict(passed=bool(armed), armed=bool(armed),
                    negative_arm="cost_channel's own blind_production_reader arm")
    except SystemExit as e:
        repo = getattr(cost_channel, "REPO", None)
        want = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
        diag = ""
        if repo is not None and os.path.abspath(repo) != want:
            diag = (" || DIAGNOSED UPSTREAM: cost_channel.REPO resolves to %r but the "
                    "repository root is %r. scripts/cost_channel.py:141 uses three '..' "
                    "from its own directory, correct only at its ORIGINAL path "
                    "verification/runs/T-family/cost_channel.py (its docstring :4-6). "
                    "The file was moved to scripts/ and the constant was not. Every "
                    "fixture path it builds is wrong, so this control CANNOT be armed "
                    "by anyone until that line is repaired. T26 registration :780-782 "
                    "makes arming it a FREEZE PRECONDITION -- so T26 CANNOT BE FROZEN "
                    "while this stands. NOT repaired from here: shared script, another "
                    "team's territory, routed to the supervisor." % (repo, want))
        return dict(passed=False, upstream_defect=bool(diag),
                    why="cost_channel refused: %s%s" % (str(e.code)[:120], diag))
    except Exception as e:
        return dict(passed=False, why="cost_channel raised %r" % (e,))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def control_dimensionality_reader():
    """D-3D, BOTH DIRECTIONS.  The positive arm plants a 3-direction line and a
    clean census.  The NEGATIVE arms are the ones that matter, and each is a
    real defect seen in this lab this week:
      * a 2-direction line MUST be caught (the T4e finding),
      * an `empty` patch MUST be caught even when checkMesh says 3,
      * an ABSENT checkMesh line MUST NOT read as a passing 3,
      * a COMMENTED-OUT line MUST NOT be read as live (the closure finding)."""
    tmp = tempfile.mkdtemp(prefix="t26_plant_3d_")
    try:
        good = os.path.join(tmp, "log.good")
        with open(good, "w") as fh:
            fh.write("Checking geometry...\n")
            fh.write("Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n")
        n, ln = read_geometric_directions(good)
        if n != 3:
            return dict(passed=False, why="the reader could not see a planted 3-direction line")
        bnd = os.path.join(tmp, "boundary")
        open(bnd, "w").write("6\n(\ninlet { type patch; }\nwall { type wall; }\n)\n")
        cen, tot = read_patch_type_census(bnd)
        v = dimensionality_verdict(n, ln, cen)
        if not v["ok"]:
            return dict(passed=False, why="a clean 3D fixture was rejected: %s" % v["why"])

        # NEGATIVE 1: two directions -- the T4e signature -- MUST be caught
        bad = os.path.join(tmp, "log.2d")
        open(bad, "w").write("Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)\n")
        n2, l2 = read_geometric_directions(bad)
        v2 = dimensionality_verdict(n2, l2, cen)
        if n2 != 2 or v2["ok"] or v2["verdict"] != "NOT A RESULT":
            return dict(passed=False, why="a 2-direction mesh was NOT caught")

        # NEGATIVE 2: an `empty` patch with checkMesh reading 3 MUST be caught
        be = os.path.join(tmp, "boundary_empty")
        open(be, "w").write("2\n(\nfront { type empty; }\nwall { type wall; }\n)\n")
        cen_e, _t = read_patch_type_census(be)
        v3 = dimensionality_verdict(3, ln, cen_e)
        if v3["ok"] or cen_e.get("empty") != 1:
            return dict(passed=False, why="an `empty` patch was NOT caught")

        # NEGATIVE 3: a wedge patch MUST be caught
        bw = os.path.join(tmp, "boundary_wedge")
        open(bw, "w").write("3\n(\na { type wedge; }\nb { type wedge; }\nc { type wall; }\n)\n")
        cen_w, _t = read_patch_type_census(bw)
        if dimensionality_verdict(3, ln, cen_w)["ok"] or cen_w.get("wedge") != 2:
            return dict(passed=False, why="a `wedge` patch was NOT caught")

        # NEGATIVE 4: ABSENT must be None, never a passing 3
        n4, l4 = read_geometric_directions(os.path.join(tmp, "no_such_log"))
        if n4 is not None or dimensionality_verdict(n4, l4, cen)["ok"]:
            return dict(passed=False, why="an ABSENT checkMesh log did not refuse")
        c4, t4 = read_patch_type_census(os.path.join(tmp, "no_such_boundary"))
        if c4 is not None or t4 != 0:
            return dict(passed=False, why="an ABSENT boundary file returned %r, not None" % c4)

        # NEGATIVE 5: a COMMENTED-OUT line must NOT be read as live.
        # This is the exact artifact that misled the closure team on 2026-09-10.
        cm = os.path.join(tmp, "log.commented")
        open(cm, "w").write("// Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n")
        n5, _l5 = read_geometric_directions(cm)
        if n5 is not None:
            return dict(passed=False, why="a COMMENTED-OUT directions line was read as LIVE "
                                          "-- the closure defect, reproduced here")
        # NEGATIVE 6: G-PROV. A log produced WITHOUT the full check set must be
        # REFUSED even when its directions line reads a perfect 3.
        weak = os.path.join(tmp, "log.weak")
        with open(weak, "w") as fh:
            fh.write("CHECKMESH COMMAND LINE: checkMesh -case /x -allRegions\n")
            fh.write("Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n")
        pw = read_checkmesh_provenance(weak)
        nw, lw = read_geometric_directions(weak)
        vw = dimensionality_verdict(nw, lw, cen, provenance=pw)
        if nw != 3 or vw["ok"] or "-allGeometry" not in vw["why"]:
            return dict(passed=False, why="a log WITHOUT -allGeometry/-allTopology was "
                                          "accepted despite a perfect 3-direction line")
        # POSITIVE: the full check set is accepted
        strong = os.path.join(tmp, "log.strong")
        with open(strong, "w") as fh:
            fh.write("CHECKMESH COMMAND LINE: checkMesh -case /x -allRegions "
                     "-allGeometry -allTopology\n")
            fh.write("Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n")
        ps = read_checkmesh_provenance(strong)
        ns, ls = read_geometric_directions(strong)
        if not dimensionality_verdict(ns, ls, cen, provenance=ps)["ok"]:
            return dict(passed=False, why="a log WITH both flags was rejected")
        # NEGATIVE 7: no command line recorded at all -> unknowable, refuse
        noprov = os.path.join(tmp, "log.noprov")
        open(noprov, "w").write("Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n")
        pn = read_checkmesh_provenance(noprov)
        if pn[0] is not None:
            return dict(passed=False, why="a provenance line was invented from nowhere")
        if dimensionality_verdict(3, ln, cen, provenance=pn)["ok"]:
            return dict(passed=False, why="a log with NO recorded command line was accepted")
        # NEGATIVE 8: a `//`-PREFIXED command line must STILL be seen. This is
        # the near-miss caught in this session: the comment stripper would have
        # erased the very line the provenance gate must read.
        pref = os.path.join(tmp, "log.prefixed")
        with open(pref, "w") as fh:
            fh.write("// CHECKMESH COMMAND LINE: checkMesh -allRegions -allGeometry "
                     "-allTopology\n")
            fh.write("Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n")
        pp = read_checkmesh_provenance(pref)
        if pp[0] is None or not (pp[1] and pp[2]):
            return dict(passed=False, why="a `//`-prefixed command line was invisible to "
                                          "the provenance reader -- the comment-stripper "
                                          "interaction is NOT defended")
        # G-MESHQ, both directions, on the REAL wording checkMesh emits
        okl = os.path.join(tmp, "log.meshok")
        open(okl, "w").write("Mesh OK.\n")
        nq, lq = read_checkmesh_failures(okl)
        if nq != 0 or not meshq_verdict(nq, lq)["ok"]:
            return dict(passed=False, why="a clean `Mesh OK.` log was rejected by G-MESHQ")
        fail = os.path.join(tmp, "log.meshfail")
        with open(fail, "w") as fh:
            fh.write(" ***Cells with small determinant (< 0.001) found, number of cells: 2320\n")
            fh.write(" ***Concave cells (using face planes) found, number of cells: 13099\n")
            fh.write("Failed 2 mesh checks.\n")
        nq, lq = read_checkmesh_failures(fail)
        vq = meshq_verdict(nq, lq)
        if nq != 2 or vq["ok"] or len(vq.get("untolerated", [])) != 2:
            return dict(passed=False, why="a `Failed 2 mesh checks` log was NOT refused "
                                          "by G-MESHQ (n=%r ok=%r)" % (nq, vq["ok"]))
        nq2, lq2 = read_checkmesh_failures(os.path.join(tmp, "no_such_log"))
        if nq2 is not None or meshq_verdict(nq2, lq2)["ok"]:
            return dict(passed=False, why="an ABSENT checkMesh log passed G-MESHQ")
        noverdict = os.path.join(tmp, "log.noverdict")
        open(noverdict, "w").write("Checking geometry...\n")
        nq3, lq3 = read_checkmesh_failures(noverdict)
        if nq3 is not None or meshq_verdict(nq3, lq3)["ok"]:
            return dict(passed=False, why="a log with NO verdict line passed G-MESHQ")

        # G-MINCELL, both directions
        big = os.path.join(tmp, "log.bigcell")
        open(big, "w").write("Min volume = 1e-9\n")     # 1e-3 m cube, well above floor
        d_ok, _v = read_min_cell_dimension(big)
        if not mincell_verdict("L2", d_ok)["ok"]:
            return dict(passed=False, why="a healthy min cell was rejected by G-MINCELL")
        tiny = os.path.join(tmp, "log.tinycell")
        open(tiny, "w").write("Min volume = 1e-18\n")   # 1e-6 m cube, far below floor
        d_bad, _v = read_min_cell_dimension(tiny)
        if mincell_verdict("L2", d_bad)["ok"]:
            return dict(passed=False, why="a SUB-FLOOR min cell was NOT caught by G-MINCELL")
        d_abs, _v = read_min_cell_dimension(os.path.join(tmp, "no_such_log"))
        if d_abs is not None or mincell_verdict("L2", d_abs)["ok"]:
            return dict(passed=False, why="an ABSENT Min volume was treated as passing")
        # REAL-FORMAT ARM: checkMesh's actual line ends in a full stop. The
        # synthetic fixtures above do not, and that is exactly how this defect
        # reached a live log before being caught.
        real = os.path.join(tmp, "log.realformat")
        open(real, "w").write("Min volume = 1.10863e-09.\n")
        d_real, v_real = read_min_cell_dimension(real)
        if d_real is None or abs(v_real - 1.10863e-09) > 1e-20:
            return dict(passed=False, why="the REAL checkMesh format `Min volume = "
                                          "1.10863e-09.` (trailing full stop) was not "
                                          "parsed: got %r" % (v_real,))
        # and an unparseable value FAILS CLOSED rather than raising
        junk = os.path.join(tmp, "log.junk")
        open(junk, "w").write("Min volume = ..\n")
        d_j, v_j = read_min_cell_dimension(junk)
        if d_j is not None or mincell_verdict("L2", d_j)["ok"]:
            return dict(passed=False, why="an unparseable Min volume did not fail closed")
        return dict(passed=True, planted="3 geometric directions + clean census",
                    negative_arms="2-direction line, empty patch, wedge patch, absent "
                                  "log, absent boundary, commented-out line, log without "
                                  "-allGeometry/-allTopology, log with no command line, "
                                  "`//`-prefixed command line, sub-floor min cell, absent "
                                  "min cell -- all eleven caught")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


CONTROLS = (("dimensionality reader (D-3D)", control_dimensionality_reader),
            ("T reader (Q1, Q2 internalField)", control_T_reader),
            ("boundary reader (Q2 interface)", control_boundary_reader),
            ("wallHeatFlux reader (Q3, G-BAL)", control_flux_reader),
            ("phi reader (G-CONT)", control_phi_reader),
            ("residual reader (G-CONV)", control_residual_reader),
            ("y+ reader (REPORTED, not gated)", control_yplus_reader),
            ("cost reader (scripts/cost_channel.py)", control_cost_reader))


def run_all_controls(verbose=True):
    """Every reader that can return a zero is shown able to see a non-zero
    BEFORE any case is read.  A failure is exit 3, not a warning."""
    results = {}
    for name, fn in CONTROLS:
        r = fn()
        results[name] = r
        if verbose:
            print("  [%s] planted control: %s%s"
                  % ("ok " if r.get("passed") else "BLIND", name,
                     "" if r.get("passed") else "  <-- " + str(r.get("why"))))
    blind = [n for n, r in results.items() if not r.get("passed")]
    return results, blind


# ===========================================================================
# ROACHE TRIPLE -- the classifier, branch for branch as analyse_t1c.py:321-337,
# with R_REFINE = 1.5 and FS = 1.25 as T26 registers them.
# ===========================================================================
def gci(f_coarse, f_med, f_fine):
    """Observed order and GCI on the finest level.  Refuses to invent an order.

    NO `GCI_pct` KEY IS RETURNED IN ANY NON-CONVERGING STATE.  That is how
    CLAUDE.md rule 5's `never quote a GCI when the three values are not
    monotone` is enforced structurally rather than by a caller remembering."""
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    if e21 == 0.0:
        return dict(state="EXACT")
    if e32 / e21 < 0.0:
        return dict(state="OSCILLATORY")
    p = math.log(abs(e32 / e21)) / math.log(R_REFINE)
    if p <= 0.0:
        return dict(state="DIVERGENT", order=p)
    if p < 0.5:
        return dict(state="STAGNANT", order=p)
    den = R_REFINE ** p - 1.0
    return dict(state="CONVERGING", order=p,
                GCI_pct=100.0 * FS * abs(e21 / f_fine) / den,
                richardson=f_fine + e21 / den)


def fmt_grid(g):
    s = g["state"]
    if "order" in g:
        s += " p=%+.3f" % g["order"]
    if "GCI_pct" in g:
        s += " GCI=%.3f %%" % g["GCI_pct"]
    return s


def verdict_t26(v1, v2, v3, band, conv_ok, plateau_ok, extra_triple=None):
    """THE RULE, as a pure function so --selftest can prove it without a case.

    `band` is (lo, hi) on the value of the FINEST level, pre-registered.
    `conv_ok` / `plateau_ok` are per-level dicts {level: bool} decided BEFORE
    this is called, exactly as the frozen T1b_L4 comparator orders it.
    `extra_triple` is the SECOND triple printed beside a NOT A RESULT, as rule
    5 clause 2 requires ("value, both triples and orders printed beside it").

    STEP 1 dominates.  STEP 3 is reached only from CONVERGING.  There is no
    path from NOT A RESULT back to PASS: the only `return` that can produce
    PASS is guarded by `g['state'] == 'CONVERGING'` AND by step 1 having
    already returned.  --selftest drives an in-band NOT A RESULT to prove it."""
    g = gci(v1, v2, v3)
    g2 = gci(*extra_triple) if extra_triple else None

    # ---- STEP 1: iteration and plateau, before any grid claim is made -------
    bad = sorted(l for l, ok in conv_ok.items() if not ok)
    flat = sorted(l for l, ok in plateau_ok.items() if not ok)
    if bad or flat:
        why = []
        if bad:
            why.append("levels " + ",".join(bad) + " not iteratively converged (G-CONV)")
        if flat:
            why.append("levels " + ",".join(flat) + " not plateaued (G-ITER)")
        return dict(verdict="NOT A RESULT", grid=g, grid_second=g2, value=v3,
                    band=band, why="; ".join(why), step=1)

    # ---- STEP 2: the triple state ------------------------------------------
    if g["state"] != "CONVERGING":
        return dict(verdict="NOT A RESULT", grid=g, grid_second=g2, value=v3,
                    band=band, step=2,
                    why=("grid triple is %s; value %.6g against band [%.6g, %.6g] "
                         "-- that is a statement about the finest mesh built, not "
                         "about a limit. No GCI is quoted: the three values are "
                         "not monotone." % (g["state"], v3, band[0], band[1])))

    # ---- STEP 3: the band, and the observed-order band ---------------------
    p = g["order"]
    if not (P_BAND[0] <= p <= P_BAND[1]):
        return dict(verdict="NOT A RESULT", grid=g, grid_second=g2, value=v3,
                    band=band, step=3,
                    why=("observed order p=%+.3f lies outside the registered band "
                         "[%.1f, %.1f]; the registration (line 581) ADDS A LEVEL "
                         "automatically rather than clamping it" % (p, P_BAND[0], P_BAND[1])))
    inside = band[0] <= v3 <= band[1]
    return dict(verdict="PASS" if inside else "GATE FAIL", grid=g, grid_second=g2,
                value=v3, band=band, step=3)


# ===========================================================================
# per-level measurement
# ===========================================================================
def cell_count_audit(counts=None):
    """Are the registered cell counts internally consistent with 3D refinement?

    A 3D mesh refined by h-ratio r steps by r**3 cells; a 2D mesh by r**2.  At
    the registered r = 1.5 those are 3.375 and 2.250 -- far enough apart that
    the RATIO ALONE discriminates.  This runs on the REGISTERED NUMBERS and
    needs no mesh, so it is available before any compute.

    ITS LIMIT, STATED: registration :456 labels these counts PROJECTIONS. This
    audit can prove the registration is NOT built on a 2D refinement pattern.
    It CANNOT prove the mesh will be 3D -- only checkMesh on a BUILT mesh can
    (D-3D above), and this function never claims otherwise."""
    c = counts or [CELLS_PROJECTED[l] for l in LEVELS]
    rows = []
    for i in range(len(c) - 1):
        N = c[i + 1] / float(c[i])
        rows.append(dict(step="%s->%s" % (LEVELS[i], LEVELS[i + 1]),
                         N_ratio=N,
                         r_if_1D=N, r_if_2D=N ** 0.5, r_if_3D=N ** (1.0 / 3.0),
                         matches_3D_at_r1p5=abs(N - 1.5 ** 3) / 1.5 ** 3 < 1e-3,
                         matches_2D_at_r1p5=abs(N - 1.5 ** 2) / 1.5 ** 2 < 1e-3))
    ok = all(r["matches_3D_at_r1p5"] for r in rows)
    return dict(consistent_with_3D=ok, counts=c, steps=rows,
                note=("PROJECTIONS, not measured cell counts (registration :456). "
                      "Consistency with a 3D refinement pattern is NECESSARY and "
                      "NOT SUFFICIENT for a 3D claim; only checkMesh on a built "
                      "mesh (D-3D) can establish dimensionality."))


def measure_level(root, level):
    case = os.path.join(root, level)
    if not os.path.isdir(case):
        refuse("no case directory for level %s at %s" % (level, case))
    if not os.path.isfile(os.path.join(root, "DONE.%s" % level)):
        refuse("no completion marker DONE.%s -- mark_done_t26.py has not passed "
               "this level under the strict completion rule, and an ungraded "
               "level is never graded around" % level)
    et = END_TIME[level]
    log = os.path.join(case, "log.solve")
    resid = read_residuals(log)
    conv = {}
    for f, gate in G_CONV.items():
        r = resid.get(f)
        conv[f] = dict(value=r, gate=gate,
                       ok=(r is not None and r <= gate),
                       measured=(r is not None))
    phi_sum, n_phi = read_phi_sum(case, et)
    q1 = read_q1_tmax(case, et)
    q2, n_q2 = read_q2_tiface(case, et)
    q3path, q3why = resolve_unique(os.path.join(case, "postProcessing", "**",
                                                "wallHeatFlux*.dat"))
    if q3path is None and "files match" in (q3why or ""):
        refuse("Q3 cannot be read: " + q3why)
    q3, n_q3 = read_wall_heat_flux(q3path, "strut") if q3path else (None, 0)
    yp, n_yp = read_yplus(os.path.join(case, "log.yPlus"))
    # D-3D: the 3D claim is carried BY THE GRADED RECORD, per level, verbatim,
    # so it can never again be an inference from a board or a geometry gate.
    cmlog = os.path.join(case, "log.checkMesh")
    ndirs, dline = read_geometric_directions(cmlog)
    census, _tot = read_patch_type_census(
        os.path.join(case, "constant", "polyMesh", "boundary"))
    prov = read_checkmesh_provenance(cmlog)
    dim = dimensionality_verdict(ndirs, dline, census, provenance=prov)
    mind, minvol = read_min_cell_dimension(cmlog)
    mincell = mincell_verdict(level, mind)
    nfail, faillines = read_checkmesh_failures(cmlog)
    meshq = meshq_verdict(nfail, faillines)
    return dict(level=level, endTime=et, Q1=q1, Q2=q2, Q2_n=n_q2, Q3=q3, Q3_n=n_q3,
                phi_sum=phi_sum, phi_n=n_phi, residuals=resid, conv=conv,
                yplus=yp, yplus_n=n_yp, dimensionality=dim, mincell=mincell,
                meshq=meshq,
                checkMesh_provenance=prov, min_cell_volume=minvol,
                conv_ok=all(c["ok"] for c in conv.values()))


# ===========================================================================
# selftest
# ===========================================================================
def selftest():
    print("analyse_t26.py --selftest")
    print("=" * 74)
    fails = []

    print("\n(i) PLANTED-ZERO CONTROLS -- every reader, both directions")
    _res, blind = run_all_controls()
    if blind:
        fails.append("planted controls blind: " + ", ".join(blind))

    print("\n(ii) THE ROACHE TRIPLE GATE -- CLAUDE.md rule 5 ordering")
    # A band placed so that the SAME value is inside it in every arm: the point
    # is that the triple STATE, not the value, decides NOT A RESULT.
    band = (99.0, 101.0)
    allok = {l: True for l in LEVELS}
    v_in = 100.0
    cases = [
        # name,                     triple (c, m, f),                expect
        # e21 = med - fine, e32 = coarse - med, and e32/e21 = r**p at r = 1.5.
        # Each arm's triple is CHOSEN to land in the state its name claims; the
        # first draft of this table mislabelled two of them and the selftest
        # caught it, which is the whole point of exercising every state.
        ("CONVERGING in band",       (103.0, 101.0, v_in),      "PASS"),        # p=+1.710
        ("CONVERGING out of band",   (108.0, 106.0, 105.0),     "GATE FAIL"),   # p=+1.710
        ("DIVERGENT, value IN band", (101.8, 101.0, v_in),      "NOT A RESULT"),  # ratio 0.8 -> p<0
        ("STAGNANT, value IN band",  (102.1293, 101.0, v_in),   "NOT A RESULT"),  # ratio 1.1293 -> p=+0.299
        ("OSCILLATORY, value IN band", (101.0, 99.0, v_in),     "NOT A RESULT"),  # ratio -2
        ("EXACT, value IN band",     (102.0, v_in, v_in),       "NOT A RESULT"),  # e21 = 0
    ]
    states = set()
    for name, tr, expect in cases:
        v = verdict_t26(tr[0], tr[1], tr[2], band, allok, allok,
                        extra_triple=(tr[0] * 1.001, tr[1], tr[2]))
        states.add(v["grid"]["state"])
        ok = v["verdict"] == expect
        fails.append(name) if not ok else None
        print("  [%s] %-30s (%.4f, %.4f, %.4f) -> %-34s -> %-13s (expected %s)"
              % ("ok " if ok else "BAD", name, tr[0], tr[1], tr[2],
                 fmt_grid(v["grid"]), v["verdict"], expect))
        # the second triple must be printed beside every NOT A RESULT (rule 5.2)
        if v["verdict"] == "NOT A RESULT" and v.get("grid_second") is None:
            fails.append(name + " printed no second triple")
        # NO GCI may be quoted on a non-monotone triple
        if v["verdict"] == "NOT A RESULT" and "GCI_pct" in v["grid"]:
            fails.append(name + " quoted a GCI on a non-CONVERGING triple")

    need = {"CONVERGING", "DIVERGENT", "OSCILLATORY", "EXACT", "STAGNANT"}
    if not need <= states:
        fails.append("states exercised %s, missing %s" % (sorted(states), sorted(need - states)))
        print("  BAD not every triple state was exercised")
    else:
        print("  ok  all five triple states exercised: %s" % ", ".join(sorted(states)))

    print("\n(iii) THE GATE IS ONE-WAY -- it turns PASS/GATE FAIL INTO NOT A RESULT,")
    print("      never the reverse.  Same value, same band, only the triple moves.")
    conv_in = verdict_t26(103.0, 101.0, v_in, band, allok, allok)
    div_in = verdict_t26(101.8, 101.0, v_in, band, allok, allok)
    one_way = (conv_in["verdict"] == "PASS" and div_in["verdict"] == "NOT A RESULT"
               and conv_in["value"] == div_in["value"]
               and div_in["grid"]["state"] == "DIVERGENT")
    print("  [%s] value %.4f INSIDE band %s: %s -> %s, %s -> %s"
          % ("ok " if one_way else "BAD", v_in, band,
             conv_in["grid"]["state"], conv_in["verdict"],
             div_in["grid"]["state"], div_in["verdict"]))
    if not one_way:
        fails.append("one-way gate")

    print("\n(iv) STEP 1 DOMINATES -- an unconverged level makes a PERFECT")
    print("     CONVERGING in-band triple a NOT A RESULT.")
    badconv = dict(allok); badconv["L3"] = False
    v = verdict_t26(103.0, 101.0, v_in, band, badconv, allok)
    ok = v["verdict"] == "NOT A RESULT" and v["step"] == 1
    print("  [%s] L3 not converged, triple CONVERGING, value in band -> %s (step %s)"
          % ("ok " if ok else "BAD", v["verdict"], v.get("step")))
    if not ok:
        fails.append("step-1 dominance")
    badflat = dict(allok); badflat["L2"] = False
    v = verdict_t26(103.0, 101.0, v_in, band, allok, badflat)
    ok = v["verdict"] == "NOT A RESULT" and v["step"] == 1
    print("  [%s] L2 not plateaued (G-ITER), triple CONVERGING, value in band -> %s (step %s)"
          % ("ok " if ok else "BAD", v["verdict"], v.get("step")))
    if not ok:
        fails.append("plateau dominance")

    print("\n(v) THE OBSERVED-ORDER BAND [%.1f, %.1f] -- outside ADDS A LEVEL" % P_BAND)
    # p > 2.5: e32/e21 = 1.5**p, so e32/e21 = 1.5**3 = 3.375 gives p = 3.
    # e21 = 1.0, so e32 must be 3.375 and coarse = v_in + 1.0 + 3.375.
    # THE FIRST DRAFT WROTE coarse = v_in + 3.375, giving e32 = 2.375 and
    # p = +2.133 -- INSIDE the band, so the code correctly returned PASS and the
    # selftest correctly called the ARM bad.  The instrument was right and the
    # test input was wrong; recorded rather than silently fixed.
    v = verdict_t26(v_in + 1.0 + 3.375, v_in + 1.0, v_in, band, allok, allok)
    ok = v["verdict"] == "NOT A RESULT" and v["grid"]["state"] == "CONVERGING"
    print("  [%s] p=%+.3f (CONVERGING but outside the band), value in band -> %s"
          % ("ok " if ok else "BAD", v["grid"].get("order", float("nan")), v["verdict"]))
    if not ok:
        fails.append("order band")

    print("\n(vi) THE REGISTERED CELL COUNTS -- 3D or 2D refinement pattern?")
    a = cell_count_audit()
    for r in a["steps"]:
        print("  %s  N = %.6f -> r would be %.4f in 1D, %.4f in 2D, %.4f in 3D  [3D at r=1.5: %s]"
              % (r["step"], r["N_ratio"], r["r_if_1D"], r["r_if_2D"], r["r_if_3D"],
                 "YES" if r["matches_3D_at_r1p5"] else "NO"))
    ok = a["consistent_with_3D"]
    print("  [%s] registered counts %s consistent with 3D refinement at r = 1.5 "
          "(N = 3.375); a 2D pattern would give N = 2.250"
          % ("ok " if ok else "BAD", "ARE" if ok else "ARE NOT"))
    if not ok:
        fails.append("cell-count 3D consistency")
    # the MUTATION: a 2D count triple must be REJECTED by the same function
    two_d = [885508, int(885508 * 2.25), int(885508 * 2.25 * 2.25)]
    m = cell_count_audit(two_d)
    ok = not m["consistent_with_3D"]
    print("  [%s] MUTATION: a 2D-pattern triple %s -> consistent_with_3D = %s (must be False)"
          % ("ok " if ok else "BAD", two_d, m["consistent_with_3D"]))
    if not ok:
        fails.append("cell-count mutation not caught")

    print("\n(vii) NO `assert` STATEMENT IN THIS FILE (L-332: -O strips them)")
    import ast
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count = %d (the counter sees a planted assert: %d)"
          % ("ok " if ok else "BAD", n_assert, planted))
    if not ok:
        fails.append("ast")

    print("\n" + "=" * 74)
    print("SELFTEST %s (%d failed)%s"
          % ("PASS" if not fails else "FAIL", len(fails),
             "" if not fails else ": " + "; ".join(sorted(set(fails)))))
    return EXIT_OK if not fails else EXIT_FAIL


# ===========================================================================
def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--audit-counts" in argv:
        a = cell_count_audit()
        for r in a["steps"]:
            print("%s  N = %.6f   r_1D %.4f   r_2D %.4f   r_3D %.4f   3D@r1.5: %s"
                  % (r["step"], r["N_ratio"], r["r_if_1D"], r["r_if_2D"],
                     r["r_if_3D"], r["matches_3D_at_r1p5"]))
        print(a["note"])
        return EXIT_OK if a["consistent_with_3D"] else EXIT_FAIL
    root = os.path.join(HERE, "..", "..", "..", "verification", "runs", "T-family", "T26_runs")
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
    root = os.path.abspath(root)

    print("T26 COMPARATOR -- VERIFICATION, NOT VALIDATION.")
    print("Reference tier for Q1, Q2 and Q3 is NONE (registration :606-613).")
    print("No absolute-accuracy claim is available from this rung and none is made.")
    print("\nPLANTED-ZERO CONTROLS (CLAUDE.md rule 3), before any case is read:")
    controls, blind = run_all_controls()
    if blind:
        refuse_blind("these readers could not see their own plants: " + ", ".join(blind))

    if not os.path.isdir(root):
        refuse("no run root %s -- T26 has not run. This is the EXPECTED state "
               "while the pre-registration is unfrozen (registration :100-114 "
               "makes the absence of this directory the rule-2 pre-compute "
               "condition)." % root)

    lv = {l: measure_level(root, l) for l in LEVELS}
    conv_ok = {l: lv[l]["conv_ok"] for l in LEVELS}

    # ---- D-3D, BEFORE any quantity is graded ------------------------------
    # T26 exists to be the genuinely 3D rung. If the BUILT mesh is not shown to
    # be 3D, the premise fails and every row is NOT A RESULT. Like the Roache
    # gate, this can only turn a verdict INTO NOT A RESULT, never the reverse.
    print("\nD-3D DIMENSIONALITY, from the BUILT mesh (never from the geometry gate):")
    not3d = []
    for l in LEVELS:
        d = lv[l]["dimensionality"]
        print("  %s  %s" % (l, d["evidence"].get("checkMesh_line") or "NO checkMesh DIRECTIONS LINE"))
        print("      patch types: %s" % (d["evidence"].get("patch_type_census") or "UNREADABLE"))
        print("      -> %s" % d["verdict"])
        if not d["ok"]:
            not3d.append(l)
            print("      %s" % d["why"])
    print("\nG-MINCELL, minimum cell dimension against the registered floor:")
    badcell = []
    for l in LEVELS:
        m = lv[l]["mincell"]
        print("  %s  min cell %s m  floor %.4g m  -> %s"
              % (l, ("%.4g" % m["dim_m"]) if m["dim_m"] is not None else "UNMEASURED",
                 m["floor_m"], m["verdict"]))
        if not m["ok"]:
            badcell.append(l)
            print("      %s" % m["why"])
    print("\nG-MESHQ, checkMesh's OWN verdict (default tolerance ZERO):")
    badq = []
    for l in LEVELS:
        q = lv[l]["meshq"]
        print("  %s  failed checks: %s -> %s" % (l, q["n_failed"], q["verdict"]))
        for x in q.get("lines", [])[:4]:
            print("      %s" % x)
        if not q["ok"]:
            badq.append(l)
            print("      %s" % q["why"])
    not3d = not3d + [l for l in badcell + badq if l not in not3d]
    if not3d:
        print("\n  THE RUNG'S PREMISE FAILS on level(s) %s. Every graded row below is"
              % ",".join(not3d))
        print("  NOT A RESULT: a verification verdict on a failed premise is not a verdict.")

    # G-ITER, the plateau gate: |dQ over the last 1000 iters| <= 0.1 x |level-to-level|
    plateau_ok = {}
    for l in LEVELS:
        p = os.path.join(root, l, "ITER_DRIFT.json")
        if not os.path.isfile(p):
            plateau_ok[l] = False
            lv[l]["plateau_why"] = ("no ITER_DRIFT.json: the G-ITER drift over the "
                                    "last 1000 iterations was never measured, and an "
                                    "unmeasured gate is not a passed gate")
        else:
            d = json.load(open(p))
            lv[l]["iter_drift_K"] = d.get("dT_max_last_1000")
            plateau_ok[l] = d.get("dT_max_last_1000") is not None

    rows = []
    for qid, key, unit in (("Q1", "Q1", "K"), ("Q2", "Q2", "K"), ("Q3", "Q3", "W")):
        vals = [lv[l][key] for l in LEVELS]
        if any(v is None for v in vals):
            rows.append(dict(row=qid, verdict="NOT A RESULT", value=None,
                             levels=dict(zip(LEVELS, vals)),
                             why="quantity ABSENT on level(s) %s -- absent is not zero"
                                 % ",".join(l for l, v in zip(LEVELS, vals) if v is None)))
            continue
        bp = os.path.join(root, "BAND_%s.json" % qid)
        if not os.path.isfile(bp):
            rows.append(dict(row=qid, verdict="NOT A RESULT", value=vals[-1],
                             levels=dict(zip(LEVELS, vals)),
                             grid=gci(*vals),
                             why="no pre-registered band BAND_%s.json; the registration "
                                 "(:606-613) registers reference tier NONE for %s, so "
                                 "there is no band and the row is graded on the triple "
                                 "and G-BAL alone" % (qid, qid)))
            continue
        b = json.load(open(bp))
        band = (b["lo"], b["hi"])
        # the second triple rule 5.2 requires printed beside a NOT A RESULT:
        # the same quantity measured at the previous checkpoint of each level
        second = tuple(lv[l].get("%s_prev" % key, lv[l][key]) for l in LEVELS)
        v = verdict_t26(vals[0], vals[1], vals[2], band, conv_ok, plateau_ok,
                        extra_triple=second)
        if not3d:
            v = dict(verdict="NOT A RESULT", value=vals[-1], grid=gci(*vals),
                     grid_second=None, band=band,
                     why="D-3D FAILED on level(s) %s: the rung's registered premise "
                         "-- that this is the genuinely 3D motor-in-duct successor "
                         "to the T23/T24 wedge -- is not established by the built "
                         "mesh. %s" % (",".join(not3d),
                                       lv[not3d[0]]["dimensionality"]["why"]),
                     step=0)
        v["row"] = qid
        v["unit"] = unit
        v["levels"] = dict(zip(LEVELS, vals))
        v["dimensionality"] = {l: lv[l]["dimensionality"] for l in LEVELS}
        rows.append(v)

    for r in rows:
        print("\n  ROW %s: value %s  %s" % (r["row"], r.get("value"),
                                            fmt_grid(r["grid"]) if r.get("grid") else ""))
        if r.get("grid_second"):
            print("        second triple: %s" % fmt_grid(r["grid_second"]))
        print("        -> %s" % r["verdict"])
        if r.get("why"):
            print("        %s" % r["why"])

    out = dict(rung="T26", Fs=FS, r=R_REFINE, rows=rows, controls=controls,
               levels=lv, cell_count_audit=cell_count_audit(),
               dimensionality={l: lv[l]["dimensionality"] for l in LEVELS},
               mincell={l: lv[l]["mincell"] for l in LEVELS},
               meshq={l: lv[l]["meshq"] for l in LEVELS},
               meshq_tolerance_registered=MESHQ_TOLERANCE,
               checkMesh_provenance={l: lv[l]["checkMesh_provenance"] for l in LEVELS},
               dimensionality_failed_levels=not3d,
               note="VERIFICATION, NOT VALIDATION -- reference tier NONE. The 3D "
                    "claim is carried by the per-level checkMesh geometric-directions "
                    "line recorded above, verbatim, and by the boundary patch-type "
                    "census -- never by the geometry gate, blockMeshDict or a board.")
    outp = argv[argv.index("--json") + 1] if "--json" in argv else os.path.join(root, "gate_t26.json")
    with open(outp, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print("\nwrote %s" % outp)
    return EXIT_FAIL if any(r["verdict"] == "GATE FAIL" for r in rows) else EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
