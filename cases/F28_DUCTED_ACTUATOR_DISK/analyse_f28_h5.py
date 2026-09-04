#!/usr/bin/env python3
"""F28 -- H5 SPATIAL-RESIDUAL COMPARATOR.  The grading path for the H5 arm.

Registered by:
  verification/campaign/F28G_H5_RESIDUAL_FIELD_PREREGISTRATION.md

WHAT IT GRADES.  Whether the cell-wise GATING initial residual of `p` (and of
`Uy`) at the parent rung's plateau is spatially CONCENTRATED, and if so WHERE.
`postProcessing/residuals/0/solverInfo.dat` cannot answer that: the scalar it
records is `gSumMag(finestResidual)/normFactor`
(GAMGSolverSolve.C:79-83) -- exactly the DENOMINATOR of the concentration ratio
and nothing else.  This comparator obtains the numerator.

IT REFUSES RATHER THAN DEGRADES.  Every check below exits 2 on failure.  A
verdict is issued only when all of them pass, and the vocabulary is fixed:
PASS / GATE FAIL / NOT A RESULT.  There is no softer word and no `PENDING`
issued from here.

THE FIELD IS THE GATING SOLVE, NOT THE CORRECTOR -- and that is why this
comparator is worth writing.  `solverInfo` never fills the residual field;
`lduMatrix.C:463-503` does, and only when `isFirstIteration()`.
`simpleControl::loop()` forces that flag true at the top of each time step and
`correctNonOrthogonal()` clears it before the non-orthogonal corrector.  So
`initialResidual:p` holds the FIRST `p` solve -- the quantity `residualControl`
actually tests, and the quantity the `res p` defect gets wrong when read by
hand.  The instrument encodes the rule; a hand-read bypasses it.

THE FIELD NAME IS A PREFIX, NOT A SUFFIX.  OpenFOAM writes
`IOobject::scopedName("initialResidual", f)` -- `initialResidual:p` on this box.
A suffix matcher of the shape `.*Residual$` matches NONE of
`initialResidual:p`, `initialResidual_p`, `initialResidualp`, and matches
`pResidual`, which the solver never writes.  That is measured, not argued, and
it is the defect this file must not repeat: `EXPECTED_FIELDS` below is built
from the prefix form and the colon is asserted, never assumed away.

CONTROLS (standing rule 3).  `--selftest` runs eight limbs, each with a
positive AND a negative side, and REFUSES unless both fire.  A zero from a
reader not shown able to see a non-zero is not evidence, and neither is a green
from a guard not shown able to go red.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import sys
import tempfile

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS.  These are the pre-registration's, and moving one of them
# is an amendment to a frozen document, not an edit to a script.
# ---------------------------------------------------------------------------
N_CELLS = 35544
N_TOP = int(0.01 * N_CELLS)                    # 355
UNIFORM_SPREAD = N_TOP / float(N_CELLS)        # 0.0099876...

G1_CONCENTRATION = 0.50        # top-1% mass fraction to call it localised
G2_ZONE_MASS = 0.60            # one zone's share of the top-1% mass
G3_MIN_SNAPSHOTS = 4           # of 5

PLATEAU_LO, PLATEAU_HI = 0.1171, 0.5132        # parent's last-4,000 band
RATIO_TOL = 1.0e-3             # constancy of sum|r| / .dat scalar
PLANT = 1.234e-03              # standing rule 3's injected perturbation

ARM_SNAPSHOTS = [15040, 15080, 15120, 15160, 15200]
PILOT_SNAPSHOTS_T = [15072]

SENTINEL = "RESTART_SENTINEL"

# Prefix form.  `IOobject::scopedName("initialResidual", f)` with
# `scopeSeparator` = ':' (IOobject.C:43-50, Linux limb; not overridden in
# etc/controlDict on this box).  The '_' form is accepted as a fallback so that
# a platform or InfoSwitch change is a DIAGNOSED miss, not a silent zero.
RESID_BASE = "initialResidual"
GATED_FIELDS = ["p", "Uy"]
REPORTED_FIELDS = ["p", "Ux", "Uy", "Uz", "k", "omega"]

ZONE_NAMES = ["Z-DISK", "Z-DUCT", "Z-HUB", "Z-AXIS", "Z-ELSEWHERE"]


class Refuse(Exception):
    """Raised for every condition on which this comparator refuses to grade."""


# ---------------------------------------------------------------------------
# READERS
# ---------------------------------------------------------------------------

HEADER_END = re.compile(r"^// \* \* \*")


def _body(path):
    with open(path) as fh:
        text = fh.read()
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if HEADER_END.match(ln):
            return "\n".join(lines[i + 1:])
    return text


def residual_field_path(time_dir, field):
    """Locate `<time>/initialResidual:<field>`, accepting the '_' separator.

    Returns (path, separator).  Raises Refuse naming BOTH candidates if
    neither is present -- an absent field must say what it looked for, or its
    absence is indistinguishable from a reader that looked for the wrong name.
    """
    tried = []
    for sep in (":", "_"):
        cand = os.path.join(time_dir, "%s%s%s" % (RESID_BASE, sep, field))
        tried.append(cand)
        if os.path.isfile(cand):
            return cand, sep
    raise Refuse(
        "no residual field for %r in %s.  Looked for: %s.  NOTE: the name is a "
        "PREFIX (`initialResidual:p`), never a suffix (`pResidual`) -- a "
        "suffix matcher finds nothing here and its zero means nothing."
        % (field, time_dir, " and ".join(tried)))


def read_internal_scalars(path):
    """Return the internalField of a volScalarField as a list of floats."""
    body = _body(path)
    m = re.search(r"internalField\s+(nonuniform|uniform)\b", body)
    if not m:
        raise Refuse("%s: no internalField entry" % path)
    if m.group(1) == "uniform":
        mv = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", body)
        if not mv:
            raise Refuse("%s: malformed uniform internalField" % path)
        return [float(mv.group(1))] * N_CELLS
    tail = body[m.end():]
    mc = re.search(r"(\d+)\s*\(", tail)
    if not mc:
        raise Refuse("%s: no count before the value list" % path)
    n = int(mc.group(1))
    start = tail.index("(", mc.start()) + 1
    depth_end = tail.index(")", start)
    vals = tail[start:depth_end].split()
    if len(vals) != n:
        raise Refuse("%s: header says %d values, list carries %d"
                     % (path, n, len(vals)))
    return [float(v) for v in vals]


def read_labels(path):
    body = _body(path)
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        raise Refuse("%s: no label list" % path)
    n = int(m.group(1))
    start = body.index("(", m.start()) + 1
    end = body.index(")", start)
    vals = body[start:end].split()
    if len(vals) != n:
        raise Refuse("%s: header says %d labels, list carries %d"
                     % (path, n, len(vals)))
    return [int(v) for v in vals]


def read_points(path):
    body = _body(path)
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        raise Refuse("%s: no point list" % path)
    n = int(m.group(1))
    pts = re.findall(r"\(([^()]*)\)", body[m.end() - 1:])
    if len(pts) < n:
        raise Refuse("%s: expected %d points, parsed %d" % (path, n, len(pts)))
    out = []
    for s in pts[:n]:
        a, b, c = s.split()
        out.append((float(a), float(b), float(c)))
    return out


def read_faces(path):
    body = _body(path)
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        raise Refuse("%s: no face list" % path)
    n = int(m.group(1))
    faces = re.findall(r"\d+\(([^()]*)\)", body[m.end():])
    if len(faces) < n:
        raise Refuse("%s: expected %d faces, parsed %d" % (path, n, len(faces)))
    return [[int(t) for t in s.split()] for s in faces[:n]]


def cell_centres(case):
    """Approximate cell centres as the mean of each cell's DISTINCT vertices.

    HONEST LIMITATION, stated because it bounds what the zone gate can claim:
    OpenFOAM's own cell centre is volume-weighted and this is not.  For a hex
    cell the two agree exactly; for the wedge and prism cells here they differ
    by a fraction of the cell size.  The zone boundaries of the registration
    are separated from one another by centimetres and the cells near those
    boundaries are far smaller, so the difference cannot move a cell between
    zones except for cells already lying on a boundary -- and §5.3's
    precedence order, not a tie-break, decides those.
    """
    pm = os.path.join(case, "constant", "polyMesh")
    points = read_points(os.path.join(pm, "points"))
    faces = read_faces(os.path.join(pm, "faces"))
    owner = read_labels(os.path.join(pm, "owner"))
    neigh = read_labels(os.path.join(pm, "neighbour"))

    ncells = max(max(owner), max(neigh) if neigh else -1) + 1
    cp = [set() for _ in range(ncells)]
    for f, pts in enumerate(faces):
        if f < len(owner):
            cp[owner[f]].update(pts)
        if f < len(neigh):
            cp[neigh[f]].update(pts)

    centres = []
    for c in range(ncells):
        ids = cp[c]
        if not ids:
            raise Refuse("cell %d has no faces -- mesh read is wrong" % c)
        sx = sy = sz = 0.0
        for i in ids:
            p = points[i]
            sx += p[0]; sy += p[1]; sz += p[2]
        k = float(len(ids))
        centres.append((sx / k, sy / k, sz / k))
    return centres


def radius(p):
    return math.sqrt(p[1] * p[1] + p[2] * p[2])


# ---------------------------------------------------------------------------
# ZONES -- frozen at the pre-registration commit, precedence order fixed
# ---------------------------------------------------------------------------

def zone_of(centre):
    x, r = centre[0], radius(centre)
    if 0.0590 <= x <= 0.0740 and 0.0325 <= r <= 0.1275:
        return "Z-DISK"
    if 0.0000 <= x <= 0.2500 and 0.1000 <= r <= 0.1800:
        return "Z-DUCT"
    if -0.0300 <= x <= 0.2500 and r <= 0.0450:
        return "Z-HUB"
    if r <= 0.0375 and (x < -0.0300 or x > 0.2500):
        return "Z-AXIS"
    return "Z-ELSEWHERE"


# ---------------------------------------------------------------------------
# THE GATES
# ---------------------------------------------------------------------------

def concentration(values):
    """f1% -- top-N_TOP share of the summed |r|.  Returns (f1, top_indices)."""
    mags = [abs(v) for v in values]
    total = sum(mags)
    if total <= 0.0:
        raise Refuse(
            "PLANTED-ZERO LIMB REFUSES: sum|r| = 0 over %d cells.  A field of "
            "zeros is not a concentrated-nowhere answer, it is a reader or a "
            "run that produced nothing.  No verdict is issued."
            % len(values))
    ntop = max(1, int(0.01 * len(values)))
    order = sorted(range(len(values)), key=lambda i: mags[i], reverse=True)
    top = order[:ntop]
    return sum(mags[i] for i in top) / total, top


def zone_mass(values, top, centres):
    mags = [abs(values[i]) for i in top]
    tot = sum(mags)
    acc = dict((z, 0.0) for z in ZONE_NAMES)
    for i, m in zip(top, mags):
        acc[zone_of(centres[i])] += m
    return dict((z, (v / tot if tot > 0 else 0.0)) for z, v in acc.items())


# ---------------------------------------------------------------------------
# COMPLETION (standing rule 4) AND THE SENTINEL AGE GUARD (ruling 2b)
# ---------------------------------------------------------------------------

def age_guard(case, times, fields_per_time):
    """Every graded field must be strictly NEWER than the restart sentinel.

    THE ANCHOR IS THE SENTINEL, NOT `0/p` (cfd-supervisor ruling 2b).  Rule 4
    anchors on `0/T` because that file is touched LAST AT LAUNCH and therefore
    dates the run allowed to produce the answer.  In a restart, `0/p` was
    written at the PARENT'S launch, so every field this run writes is
    necessarily newer than it and the guard would pass unconditionally.  A
    vacuous guard that reports green is worse than an absent one, because it
    certifies.  `RESTART_SENTINEL` is written by `run_f28_h5.sh` as its last
    action before the solver line.
    """
    anchor = os.path.join(case, SENTINEL)
    if not os.path.isfile(anchor):
        raise Refuse(
            "age guard has no anchor: %s is missing.  The launcher must write "
            "it as its LAST action before the solver line; without it the "
            "guard cannot date the run and no verdict is issued." % anchor)
    t_anchor = os.path.getmtime(anchor)
    stale = []
    for t in times:
        for f in fields_per_time:
            p, _sep = residual_field_path(os.path.join(case, str(t)), f)
            if os.path.getmtime(p) <= t_anchor:
                stale.append(p)
    if stale:
        raise Refuse(
            "AGE GUARD REFUSES: %d field(s) are NOT newer than %s -- they "
            "predate the run that was supposed to produce them: %s"
            % (len(stale), SENTINEL, ", ".join(stale[:5])))
    return t_anchor


def completion(case, end_time, n_iter, fields_per_time, times):
    """The seven clauses.  Any failure is NOT A RESULT, never a soft word."""
    problems = []
    log = os.path.join(case, "log.simpleFoam")
    if not os.path.isfile(log):
        return ["log.simpleFoam missing"]
    with open(log, errors="replace") as fh:
        text = fh.read()

    if not re.search(r"^End\s*$", text, re.M):
        problems.append("no End line in log.simpleFoam")

    exec_n = len(re.findall(r"^ExecutionTime = ", text, re.M))
    if exec_n != n_iter:
        problems.append(
            "ExecutionTime count %d != endTime - startTime = %d  (clause 5 is "
            "the RESTART form, approved by cfd-supervisor ruling 2a; the "
            "standing form `count == endTime` is its startTime = 0 case)"
            % (exec_n, n_iter))

    tms = [int(m.group(1)) for m in re.finditer(r"^Time = (\d+)", text, re.M)]
    if not tms:
        problems.append("no Time lines in log.simpleFoam")
    elif tms[-1] != end_time:
        problems.append("last time %d != endTime %d" % (tms[-1], end_time))

    for t in times:
        td = os.path.join(case, str(t))
        if not os.path.isdir(td):
            problems.append("time directory %s missing" % td)
            continue
        for f in fields_per_time:
            try:
                residual_field_path(td, f)
            except Refuse as e:
                problems.append(str(e))

    end_dir = os.path.join(case, str(end_time))
    for f in ("U", "p", "k", "omega", "nut", "phi"):
        if not os.path.isfile(os.path.join(end_dir, f)):
            problems.append("solution field %s missing at endTime" % f)

    status = [n for n in os.listdir(case) if n.startswith("RUN_STATUS.")]
    if not status:
        problems.append("no RUN_STATUS file")
    else:
        st = open(os.path.join(case, status[0])).read()
        if "solver_rc=0" not in st:
            problems.append("RUN_STATUS does not carry solver_rc=0")
        if "parent_immutable=verified_before_and_after" not in st:
            problems.append(
                "RUN_STATUS does not record the parent immutability check -- "
                "the graded rung's evidence was not proved unchanged")
    return problems


# ---------------------------------------------------------------------------
# THE CONNECTION LIMB -- ties the field to a number already on the record
# ---------------------------------------------------------------------------

def dat_scalars(case, field, times):
    """First-solve initial residual per iteration from solverInfo.dat.

    AMENDMENT 2, 2026-09-04, BEFORE FIRST COMPUTE.  As first written this
    hardcoded `postProcessing/residuals/0/`.  That is the PARENT'S directory
    name, because the parent started at time 0.  **A restart from 15000 writes
    `postProcessing/residuals/15000/`**, so the hardcoded path would have been
    missing on every run this comparator exists to grade, and the comparator
    would have refused every arm for a reason that was its own.  It now scans
    every time-named subdirectory and merges their rows, which is also correct
    if a run is ever restarted twice.
    """
    base = os.path.join(case, "postProcessing", "residuals")
    if not os.path.isdir(base):
        raise Refuse("no postProcessing/residuals directory under %s" % case)
    dats = []
    for sub in sorted(os.listdir(base)):
        cand = os.path.join(base, sub, "solverInfo.dat")
        if os.path.isfile(cand):
            dats.append(cand)
    if not dats:
        raise Refuse(
            "no solverInfo.dat under %s (looked in every time subdirectory; "
            "a restart writes it under its startTime, not under 0)" % base)
    header, rows = None, {}
    for dat in dats:
        with open(dat) as fh:
            for ln in fh:
                if ln.startswith("#"):
                    if "Time" in ln:
                        header = ln.lstrip("#").split()
                    continue
                parts = ln.split()
                if parts:
                    rows[int(float(parts[0]))] = parts
    if header is None:
        raise Refuse("solverInfo.dat carries no column header")
    col = "%s_initial" % field
    if col not in header:
        raise Refuse("solverInfo.dat has no column %r (has: %s)"
                     % (col, " ".join(header)))
    idx = header.index(col)
    out = {}
    for t in times:
        if t not in rows:
            raise Refuse("solverInfo.dat has no row for iteration %d" % t)
        out[t] = float(rows[t][idx])
    return out


def connection_limb(sums, scalars, times):
    """sum|r| = normFactor x (.dat scalar).  normFactor is not written to any
    artifact, so the ABSOLUTE value cannot be checked and this limb checks the
    RATIO IS CONSTANT across snapshots instead.  Stated as the weaker check it
    is."""
    ratios = []
    for t in times:
        s = scalars[t]
        if s <= 0:
            raise Refuse("solverInfo.dat scalar at %d is %r" % (t, s))
        ratios.append(sums[t] / s)
    lo, hi = min(ratios), max(ratios)
    spread = (hi - lo) / hi if hi > 0 else 1.0
    if spread > RATIO_TOL:
        raise Refuse(
            "CONNECTION LIMB REFUSES: sum|r| / (.dat scalar) is not constant "
            "across snapshots -- spread %.3e exceeds %.3e.  ratios=%s.  The "
            "field is not the quantity the .dat records: it may be stale, "
            "read with a wrong cell count, or taken from the corrector solve."
            % (spread, RATIO_TOL, ["%.6g" % r for r in ratios]))
    return ratios


def injected_perturbation_limb(field_path):
    """Plant a KNOWN value into a SCRATCH COPY and require it back.

    A reader that cannot see a planted value has not earned its zeros.  The
    copy is what keeps this off the graded artifact.
    """
    tmp = tempfile.mkdtemp(prefix="f28h5_plant_")
    try:
        dst = os.path.join(tmp, "planted")
        shutil.copy2(field_path, dst)
        vals = read_internal_scalars(dst)
        idx = len(vals) // 3
        original = vals[idx]
        vals[idx] = PLANT
        body = _body(dst)
        m = re.search(r"internalField\s+nonuniform[^(]*\(", body)
        if not m:
            raise Refuse("plant limb: cannot locate the value list to rewrite")
        head = open(dst).read()
        cut = head.index("(", head.index("internalField"))
        end = head.index(")", cut)
        new = (head[:cut + 1] + "\n"
               + "\n".join(repr(v) for v in vals) + "\n"
               + head[end:])
        open(dst, "w").write(new)
        back = read_internal_scalars(dst)
        if abs(back[idx] - PLANT) > 1e-15:
            raise Refuse(
                "PLANT LIMB REFUSES: wrote %r at index %d and read back %r.  "
                "The reader cannot see a value it was shown; its zeros are "
                "not evidence." % (PLANT, idx, back[idx]))
        if abs(back[idx] - original) < 1e-30 and original != PLANT:
            raise Refuse("PLANT LIMB REFUSES: the plant did not take effect")
        return idx
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# GRADING
# ---------------------------------------------------------------------------

def grade(case, mode):
    times = ARM_SNAPSHOTS if mode == "arm" else PILOT_SNAPSHOTS_T
    end_time = times[-1]
    n_iter = 200 if mode == "arm" else 72

    print("case  : %s" % case)
    print("mode  : %s   snapshots: %s" % (mode, times))
    print("")

    if mode != "arm":
        print("NOT A RESULT -- BY CONSTRUCTION, NOT BY OUTCOME.")
        print("  The pilot is a COST-MEASUREMENT INSTRUMENT.  Gates G1/G2/G3 "
              "each require agreement across %d of %d snapshots and the pilot "
              "writes %d.  It cannot satisfy them whatever its field "
              "contains, and no physics verdict may be read off it."
              % (G3_MIN_SNAPSHOTS, len(ARM_SNAPSHOTS), len(times)))
        print("")
        print("  What the pilot IS graded on: that the field exists, is "
              "readable WITH A COLON IN ITS FILENAME, carries %d values, is "
              "not all zeros, and ties to solverInfo.dat." % N_CELLS)
        print("")

    # --- clause 0: the field exists at all, and under which separator -------
    seps = set()
    for t in times:
        for f in REPORTED_FIELDS:
            _p, sep = residual_field_path(os.path.join(case, str(t)), f)
            seps.add(sep)
    print("residual field separator observed: %s" % sorted(seps))
    if ":" not in seps:
        print("  NOTE: the ':' form was NOT observed.  The registration "
              "inferred it from IOobject.C:43-50 and had never seen one "
              "produced on this box.  This is the finding, not a detail.")

    problems = completion(case, end_time, n_iter, REPORTED_FIELDS, times)
    if problems:
        print("NOT A RESULT -- strict completion (standing rule 4) failed:")
        for p in problems:
            print("   - %s" % p)
        return 1

    age_guard(case, times, REPORTED_FIELDS)
    print("age guard: PASS (anchor %s)" % SENTINEL)

    centres = cell_centres(case)
    if len(centres) != N_CELLS:
        raise Refuse("mesh carries %d cells, registration froze %d"
                     % (len(centres), N_CELLS))

    verdicts = {}
    for field in GATED_FIELDS:
        sums, f1s, zones = {}, {}, {}
        for t in times:
            path, _sep = residual_field_path(os.path.join(case, str(t)), field)
            vals = read_internal_scalars(path)
            if len(vals) != N_CELLS:
                raise Refuse("%s carries %d values, expected %d"
                             % (path, len(vals), N_CELLS))
            sums[t] = sum(abs(v) for v in vals)
            f1, top = concentration(vals)
            f1s[t] = f1
            zones[t] = zone_mass(vals, top, centres)
        injected_perturbation_limb(
            residual_field_path(os.path.join(case, str(times[0])), field)[0])
        scal = dat_scalars(case, field, times)
        connection_limb(sums, scal, times)

        # plateau refusal applies to p, the gated quantity of the record
        if field == "p":
            for t in times:
                if not (PLATEAU_LO <= scal[t] <= PLATEAU_HI):
                    print("NOT A RESULT -- plateau refusal: gating p residual "
                          "%.6g at iteration %d is outside the parent's "
                          "measured last-4,000 band [%g, %g].  This run did "
                          "not sample the plateau the record gates on."
                          % (scal[t], t, PLATEAU_LO, PLATEAU_HI))
                    return 1

        n_conc = sum(1 for t in times if f1s[t] >= G1_CONCENTRATION)
        print("")
        print("field %s" % field)
        for t in times:
            best = max(zones[t].items(), key=lambda kv: kv[1])
            print("  iter %-6d f1%%=%.4f (uniform would be %.4f)  "
                  "top zone %s at %.3f"
                  % (t, f1s[t], UNIFORM_SPREAD, best[0], best[1]))
        if n_conc < G3_MIN_SNAPSHOTS:
            print("  G1 GATE FAIL: concentrated in %d of %d snapshots, "
                  "threshold %d.  The plateau residual is DIFFUSE."
                  % (n_conc, len(times), G3_MIN_SNAPSHOTS))
            print("  This is an INFORMATIVE NEGATIVE, registered as such: a "
                  "diffuse residual has no local source, which is evidence "
                  "AGAINST H4 and leaves H1 and H3 standing.")
            verdicts[field] = "GATE FAIL"
            continue
        winners = {}
        for t in times:
            best = max(zones[t].items(), key=lambda kv: kv[1])
            if best[1] >= G2_ZONE_MASS:
                winners[t] = best[0]
        tally = {}
        for z in winners.values():
            tally[z] = tally.get(z, 0) + 1
        top_zone = max(tally.items(), key=lambda kv: kv[1]) if tally else None
        if top_zone is None or top_zone[1] < G3_MIN_SNAPSHOTS:
            print("  G2 GATE FAIL: MULTI-ZONE.  Concentrated, but no single "
                  "zone carries >= %.2f of the top-1%% mass in >= %d of %d "
                  "snapshots." % (G2_ZONE_MASS, G3_MIN_SNAPSHOTS, len(times)))
            verdicts[field] = "GATE FAIL"
            continue
        print("  PASS: localised in %s (%d of %d snapshots)"
              % (top_zone[0], top_zone[1], len(times)))
        verdicts[field] = "PASS -- %s" % top_zone[0]

    print("")
    for f in GATED_FIELDS:
        print("VERDICT %-4s : %s" % (f, verdicts.get(f, "NOT A RESULT")))
    if verdicts.get("p", "").startswith("PASS") != \
       verdicts.get("Uy", "").startswith("PASS"):
        print("REPORTED: the p and Uy localisations DISAGREE.  Registered as "
              "a named outcome; it is not dropped for being inconvenient.")
    return 0


# ---------------------------------------------------------------------------
# SELFTEST -- eight limbs, each positive AND negative
# ---------------------------------------------------------------------------

def _write_scalar_field(path, vals):
    with open(path, "w") as fh:
        fh.write("FoamFile{version 2.0;format ascii;class volScalarField;}\n")
        fh.write("// * * *\n")
        fh.write("internalField   nonuniform List<scalar>\n%d\n(\n" % len(vals))
        fh.write("\n".join(repr(v) for v in vals))
        fh.write("\n)\n;\n")


def selftest():
    fails = []

    def check(name, cond, detail=""):
        if cond:
            print("  PASS  %s" % name)
        else:
            print("  FAIL  %s  %s" % (name, detail))
            fails.append(name)

    print("LIMB 1 -- the colon in the filename")
    d = tempfile.mkdtemp(prefix="f28h5_")
    td = os.path.join(d, "15040"); os.makedirs(td)
    _write_scalar_field(os.path.join(td, "initialResidual:p"), [1.0, 2.0])
    try:
        p, sep = residual_field_path(td, "p")
        check("reads a file literally named initialResidual:p", sep == ":")
    except Refuse as e:
        check("reads a file literally named initialResidual:p", False, str(e))
    # NEGATIVE: the suffix form the census hunted must NOT be accepted.
    td2 = os.path.join(d, "15080"); os.makedirs(td2)
    _write_scalar_field(os.path.join(td2, "pResidual"), [1.0])
    try:
        residual_field_path(td2, "p")
        check("refuses the suffix form `pResidual`", False,
              "it was accepted; this reader would repeat the census defect")
    except Refuse:
        check("refuses the suffix form `pResidual`", True)

    print("LIMB 2 -- the suffix pattern really cannot match the real names")
    pat = re.compile(r"^[A-Za-z][A-Za-z0-9_.]*Residual$")
    check("`.*Residual$` matches none of the prefix forms",
          not pat.match("initialResidual:p")
          and not pat.match("initialResidual_p")
          and not pat.match("initialResidualp"))
    check("`.*Residual$` DOES match pResidual (so the plant was shaped like "
          "the bug)", bool(pat.match("pResidual")))

    print("LIMB 3 -- concentration gate")
    conc = [0.0] * 1000
    for i in range(10):
        conc[i] = 10.0
    for i in range(10, 1000):
        conc[i] = 0.001
    f1, _top = concentration(conc)
    check("a concentrated field passes G1", f1 >= G1_CONCENTRATION,
          "f1=%.4f" % f1)
    unif = [1.0] * 1000
    f1u, _ = concentration(unif)
    check("a uniform field FAILS G1", f1u < G1_CONCENTRATION,
          "f1=%.4f" % f1u)
    check("a uniform field reads at the uniform-spread value",
          abs(f1u - 0.01) < 1e-9, "f1=%.6f" % f1u)

    print("LIMB 4 -- the planted-zero refusal")
    try:
        concentration([0.0] * 100)
        check("an all-zero field is REFUSED", False, "it was graded")
    except Refuse:
        check("an all-zero field is REFUSED", True)
    try:
        f1n, _ = concentration([0.0] * 99 + [1e-30])
        check("a field with one tiny non-zero is NOT refused", True)
    except Refuse as e:
        check("a field with one tiny non-zero is NOT refused", False, str(e))

    print("LIMB 5 -- zone assignment and its precedence")
    check("disk centre -> Z-DISK", zone_of((0.0665, 0.08, 0.0)) == "Z-DISK")
    check("duct band -> Z-DUCT", zone_of((0.15, 0.13, 0.0)) == "Z-DUCT")
    check("hub -> Z-HUB", zone_of((0.10, 0.02, 0.0)) == "Z-HUB")
    check("far downstream axis -> Z-AXIS", zone_of((3.0, 0.01, 0.0)) == "Z-AXIS")
    check("freestream -> Z-ELSEWHERE",
          zone_of((3.0, 2.0, 0.0)) == "Z-ELSEWHERE")
    # PRECEDENCE: a point inside BOTH the disk collar and the duct band must
    # resolve to Z-DISK, because Z-DISK is tested first.
    both = (0.0665, 0.12, 0.0)
    check("overlap resolves by precedence to Z-DISK",
          zone_of(both) == "Z-DISK",
          "got %s" % zone_of(both))
    # NEGATIVE on the radius formula: a point whose radius is carried entirely
    # by z must be classified by r, not by y.  y=0 alone would read Z-HUB.
    check("radius uses sqrt(y^2+z^2), not |y|",
          zone_of((0.15, 0.0, 0.13)) == "Z-DUCT",
          "got %s -- a |y| reader returns Z-HUB" % zone_of((0.15, 0.0, 0.13)))

    print("LIMB 6 -- the sentinel age guard (ruling 2b)")
    import time as _t
    g = tempfile.mkdtemp(prefix="f28h5_age_")
    gt = os.path.join(g, "15040"); os.makedirs(gt)
    # NEGATIVE FIRST: field written BEFORE the sentinel must be REFUSED.
    _write_scalar_field(os.path.join(gt, "initialResidual:p"), [1.0])
    _t.sleep(0.05)
    open(os.path.join(g, SENTINEL), "w").write("now\n")
    try:
        age_guard(g, [15040], ["p"])
        check("a field OLDER than the sentinel is REFUSED", False,
              "it passed -- the guard is vacuous")
    except Refuse:
        check("a field OLDER than the sentinel is REFUSED", True)
    # POSITIVE: touch the field after the sentinel; must pass.
    _t.sleep(0.05)
    _write_scalar_field(os.path.join(gt, "initialResidual:p"), [1.0])
    try:
        age_guard(g, [15040], ["p"])
        check("a field NEWER than the sentinel passes", True)
    except Refuse as e:
        check("a field NEWER than the sentinel passes", False, str(e))
    # AND: a missing sentinel must refuse, not default to green.
    os.remove(os.path.join(g, SENTINEL))
    try:
        age_guard(g, [15040], ["p"])
        check("a MISSING sentinel is REFUSED", False, "it passed")
    except Refuse:
        check("a MISSING sentinel is REFUSED", True)
    # AND THE VACUITY DEMONSTRATION: the anchor the supervisor refused.
    # `0/p` is inherited from the parent's launch, so it is older than
    # everything and would pass unconditionally.  Shown, not asserted.
    z = tempfile.mkdtemp(prefix="f28h5_vac_")
    os.makedirs(os.path.join(z, "0")); os.makedirs(os.path.join(z, "15040"))
    open(os.path.join(z, "0", "p"), "w").write("inherited\n")
    _t.sleep(0.05)
    _write_scalar_field(os.path.join(z, "15040", "initialResidual:p"), [0.0])
    old_anchor = os.path.getmtime(os.path.join(z, "0", "p"))
    new_field = os.path.getmtime(
        os.path.join(z, "15040", "initialResidual:p"))
    check("an inherited 0/p anchor WOULD have passed unconditionally "
          "(why ruling 2b refused it)", new_field > old_anchor)

    print("LIMB 7 -- the injected perturbation")
    pf = os.path.join(td, "initialResidual:p")
    _write_scalar_field(pf, [0.5] * 30)
    try:
        idx = injected_perturbation_limb(pf)
        check("PLANT is written and read back through the real reader",
              idx is not None)
    except Refuse as e:
        check("PLANT is written and read back through the real reader",
              False, str(e))
    check("the graded artifact was NOT modified by the plant",
          read_internal_scalars(pf) == [0.5] * 30)

    print("LIMB 8 -- the connection limb")
    times = [1, 2, 3]
    ok_sums = {1: 10.0, 2: 20.0, 3: 30.0}
    ok_scal = {1: 1.0, 2: 2.0, 3: 3.0}
    try:
        connection_limb(ok_sums, ok_scal, times)
        check("a constant ratio passes", True)
    except Refuse as e:
        check("a constant ratio passes", False, str(e))
    bad_sums = {1: 10.0, 2: 20.0, 3: 45.0}
    try:
        connection_limb(bad_sums, ok_scal, times)
        check("a drifting ratio is REFUSED", False, "it passed")
    except Refuse:
        check("a drifting ratio is REFUSED", True)

    print("LIMB 9 -- solverInfo.dat is found under the RESTART time, not 0")
    # A restart from 15000 writes postProcessing/residuals/15000/, never /0/.
    # The first draft of this comparator hardcoded /0/ and would have refused
    # every arm it exists to grade, for a reason that was its own.
    rr = tempfile.mkdtemp(prefix="f28h5_pp_")
    pp = os.path.join(rr, "postProcessing", "residuals", "15000")
    os.makedirs(pp)
    with open(os.path.join(pp, "solverInfo.dat"), "w") as fh:
        fh.write("# Solver information\n")
        fh.write("# Time\tUx_initial\tUy_initial\tp_initial\n")
        fh.write("15040\t1.0\t0.25\t0.30\n")
    try:
        got = dat_scalars(rr, "p", [15040])
        check("reads solverInfo.dat from postProcessing/residuals/15000",
              abs(got[15040] - 0.30) < 1e-12, "got %r" % got)
        gy = dat_scalars(rr, "Uy", [15040])
        check("column selection picks Uy_initial, not the first numeric column",
              abs(gy[15040] - 0.25) < 1e-12, "got %r" % gy)
    except Refuse as e:
        check("reads solverInfo.dat from postProcessing/residuals/15000",
              False, str(e))
    # NEGATIVE: no .dat anywhere must REFUSE, not return an empty answer.
    shutil.rmtree(os.path.join(rr, "postProcessing", "residuals", "15000"))
    try:
        dat_scalars(rr, "p", [15040])
        check("a missing solverInfo.dat is REFUSED", False, "it passed")
    except Refuse:
        check("a missing solverInfo.dat is REFUSED", True)
    shutil.rmtree(rr, ignore_errors=True)

    for tmp in (d, g, z):
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    if fails:
        print("SELFTEST REFUSED: %d limb(s) failed: %s"
              % (len(fails), ", ".join(fails)))
        return 2
    print("SELFTEST PASS: all limbs fired on both sides.")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 3:
        print(__doc__)
        print("usage: analyse_f28_h5.py <runRoot> --mode {pilot|arm}")
        print("       analyse_f28_h5.py --selftest")
        return 1
    case = argv[1]
    mode = argv[argv.index("--mode") + 1] if "--mode" in argv else "arm"
    try:
        return grade(case, mode)
    except Refuse as e:
        print("REFUSED (exit 2): %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
