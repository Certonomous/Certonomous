#!/usr/bin/env python3
"""
JF1 -- READERS AND DISK PLANTS for the jet-flap comparator.

Every reader in this file is a reader that PRODUCES A GRADED NUMBER, and every
plant in this file WRITES INTO A REAL FILE ON DISK and is read back through the
SAME reader that grades.  That is the whole point of the module boundary: a
plant that perturbs a Python list in memory certifies nothing, and a plant that
certifies a reader whose value never reaches a graded number certifies nothing
either.  The pairing is stated once, here, and is asserted mechanically by
`analyse_jf1.py::control_plants_certify_graded_readers()`:

    reader                          graded quantity it produces
    ------------------------------  ------------------------------------------
    read_cl()                       CL_aero -> CL_total  (gate G comparand,
                                    gate THEORY (a) and (b) comparand)
    read_jet_sum_phi()              sum(phi) over jetSlot -> the jet mass-flow
                                    relative mismatch (JF1_PREREGISTRATION.md
                                    section 7.4, section 8.4 refusal 11)
    read_cl() -> theory_rel_diff()  the gate THEORY relative difference

REFUSAL DISCIPLINE: `raise` only in this module (the caller converts to
exit 2); ZERO `assert` statements, checked by AST from the comparator (L-332).

Model: JF1_PREREGISTRATION.md, FROZEN, blob
66543c97fa1527ef7c36f0980460fcc0ca348508.  This file is a TRANSCRIPTION of that
document and departs from it nowhere silently.
"""
import os
import re
import math
import shutil

import numpy as np

# `nan`, `inf`, `-inf` are included DELIBERATELY.  OpenFOAM writes them into
# ascii fields when a solution blows up, and section 8.4 requires the comparator
# to REFUSE on `U` containing NaN or Inf.  A number regex that cannot match them
# turns that registered refusal into a parse error with the wrong reason.
_NUM = r"[-+]?(?:nan|inf|(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)"


class FoamReadError(Exception):
    pass


# ---------------------------------------------------------------------------
# TEXT UTILITIES
# ---------------------------------------------------------------------------
def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def strip_top_level_block(text, key):
    """Remove a brace-matched top-level `key { ... }` block.

    THIS IS LOAD-BEARING AND IS NOT TIDINESS.  `system/controlDict` carries a
    `functions { ... }` block whose function objects contain their OWN
    `writeControl` and `writeInterval` entries -- in the real JF1 substrate,
    `writeControl timeStep; writeInterval 1;` inside `forceCoeffs`.  Section
    8.1 clause 3 pins the CASE's `writeInterval` at 20000.  A regex that scans
    the whole file finds the function object's `1` and either refuses a
    conforming case or, worse, accepts a non-conforming one whose function
    object happens to read 20000.  The pin is read from the file with every
    top-level `functions` block removed.
    """
    m = re.search(r"\b%s\s*\{" % re.escape(key), text)
    if not m:
        return text
    depth, i = 1, m.end()
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    if depth:
        raise FoamReadError("unbalanced `%s {` block" % key)
    return text[:m.start()] + text[i:]


def _entry(text, key):
    m = re.search(r"^\s*%s\s+([^;{}]+);" % re.escape(key), text, re.M)
    return m.group(1).strip() if m else None


# ---------------------------------------------------------------------------
# DICTIONARIES -- section 8.1 clause 3, the PIN
# ---------------------------------------------------------------------------
def read_control_dict(path):
    """Return the five pinned top-level termination entries of section 8.1
    clause 3 (JF1_PREREGISTRATION.md:1612-1616), with the `functions` block
    removed first.  Missing entries come back as None so the caller refuses
    with the key name rather than with a parse error."""
    if not os.path.isfile(path):
        raise FoamReadError("no controlDict at %s" % path)
    text = strip_top_level_block(strip_comments(open(path).read()), "functions")
    out = {}
    for key in ("startTime", "deltaT", "endTime", "writeControl", "writeInterval"):
        out[key] = _entry(text, key)
    return out


def read_residual_control(path):
    """Return the four `residualControl` keys of section 5.5 / 8.1 clause 3
    from `system/fvSolution` (JF1_PREREGISTRATION.md:1616-1618)."""
    if not os.path.isfile(path):
        raise FoamReadError("no fvSolution at %s" % path)
    text = strip_comments(open(path).read())
    m = re.search(r"residualControl\s*\{", text)
    if not m:
        raise FoamReadError("%s: no residualControl block" % path)
    depth, i = 1, m.end()
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    if depth:
        raise FoamReadError("%s: unbalanced residualControl block" % path)
    body = text[m.end():i - 1]
    out = {}
    for km in re.finditer(r"(\w+)\s+(%s)\s*;" % _NUM, body):
        out[km.group(1)] = km.group(2)
    return out


# ---------------------------------------------------------------------------
# FIELDS -- section 8.1 clause 4, and section 8.4's NaN/Inf and realisability
# ---------------------------------------------------------------------------
def _parse_list(text, start, kind):
    m = re.compile(r"\s*(\d+)\s*\(", re.S).match(text, start)
    if not m:
        raise FoamReadError("expected `N (` at offset %d" % start)
    n = int(m.group(1))
    pos = m.end()
    if kind == "vector":
        pat = re.compile(r"\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM))
        out = np.empty((n, 3))
        for k in range(n):
            mm = pat.match(text, pos)
            if not mm:
                raise FoamReadError("vector list: bad entry %d of %d" % (k, n))
            out[k] = (float(mm.group(1)), float(mm.group(2)), float(mm.group(3)))
            pos = mm.end()
    else:
        pat = re.compile(r"\s*(%s)" % _NUM)
        out = np.empty(n)
        for k in range(n):
            mm = pat.match(text, pos)
            if not mm:
                raise FoamReadError("scalar list: bad entry %d of %d" % (k, n))
            out[k] = float(mm.group(1))
            pos = mm.end()
    mm = re.compile(r"\s*\)").match(text, pos)
    if not mm:
        raise FoamReadError("list of %d entries not closed" % n)
    return out, mm.end()


def _uniform_value(inner, kind):
    if kind == "vector":
        m = re.search(r"uniform\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM), inner)
        if m:
            return np.array([[float(m.group(1)), float(m.group(2)), float(m.group(3))]])
    else:
        m = re.search(r"uniform\s+(%s)" % _NUM, inner)
        if m:
            return np.array([float(m.group(1))])
    return None


def read_field(path):
    """Return dict(kind, internal, patches, raw_patches, path).

    `patches[name]` carries the numeric `value` (uniform broadcast to one row,
    or the nonuniform list); `raw_patches[name]` carries the entry's RAW TEXT,
    which is what section 1.6a's `bytewise identical` assertion compares."""
    if not os.path.isfile(path):
        raise FoamReadError("no field file at %s" % path)
    raw = open(path).read()
    text = strip_comments(raw)
    m = re.search(r"class\s+(volVectorField|volScalarField)\s*;", text)
    if not m:
        raise FoamReadError("%s: not a volVectorField or volScalarField" % path)
    kind = "vector" if m.group(1) == "volVectorField" else "scalar"
    m = re.search(r"internalField\s+nonuniform\s+List<(vector|scalar)>", text)
    if m:
        internal, pos = _parse_list(text, m.end(), kind)
    else:
        mu = re.search(r"internalField\s+uniform\s+", text)
        if not mu:
            raise FoamReadError("%s: no internalField" % path)
        internal, pos = _uniform_value(text[mu.start():], kind), mu.end()
        if internal is None:
            raise FoamReadError("%s: unreadable uniform internalField" % path)
    patches, raw_patches = {}, {}
    mb = re.search(r"boundaryField\s*\{", text[pos:])
    if mb:
        body = text[pos + mb.end():]
        for pm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
            name, inner = pm.group(1), pm.group(2)
            raw_patches[name] = inner
            mv = re.search(r"value\s+nonuniform\s+List<(vector|scalar)>", inner)
            if mv:
                patches[name], _ = _parse_list(inner, mv.end(), kind)
            else:
                mvu = re.search(r"value\s+uniform", inner)
                patches[name] = _uniform_value(inner[mvu.start():], kind) if mvu else None
    return dict(kind=kind, internal=internal, patches=patches,
                raw_patches=raw_patches, path=path)


def patch_entry_text(field, patch, key):
    """The RAW text of `key ...;` inside one patch entry -- section 1.6a
    compares the `jetSlot` `value` entry BYTEWISE across the alpha sweep, so
    this returns text and never a parsed number."""
    inner = field["raw_patches"].get(patch)
    if inner is None:
        raise FoamReadError("%s: no `%s` patch in boundaryField" % (field["path"], patch))
    m = re.search(r"\b%s\b[^;]*;" % re.escape(key), inner)
    if not m:
        raise FoamReadError("%s: patch `%s` has no `%s` entry" % (field["path"], patch, key))
    return m.group(0)


def patch_vector(field, patch, key="value"):
    inner = field["raw_patches"].get(patch)
    if inner is None:
        raise FoamReadError("%s: no `%s` patch" % (field["path"], patch))
    m = re.search(r"\b%s\s+uniform\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)"
                  % (re.escape(key), _NUM, _NUM, _NUM), inner)
    if not m:
        raise FoamReadError("%s: patch `%s` has no uniform vector `%s`"
                            % (field["path"], patch, key))
    return np.array([float(m.group(1)), float(m.group(2)), float(m.group(3))])


# ---------------------------------------------------------------------------
# forceCoeffs -- THE `CL` READER (Plant 1, and the gate G / gate THEORY value)
# ---------------------------------------------------------------------------
def coefficient_dat_path(case_dir):
    """`postProcessing/forceCoeffs*/*/coefficient.dat` (section 8.2 Plant 1's
    own wording).  Refuses on ambiguity rather than picking one."""
    root = os.path.join(case_dir, "postProcessing")
    hits = []
    if os.path.isdir(root):
        for fo in sorted(os.listdir(root)):
            if not fo.startswith("forceCoeffs"):
                continue
            fod = os.path.join(root, fo)
            if not os.path.isdir(fod):
                continue
            for sub in sorted(os.listdir(fod)):
                p = os.path.join(fod, sub, "coefficient.dat")
                if os.path.isfile(p):
                    hits.append(p)
    if not hits:
        raise FoamReadError("no postProcessing/forceCoeffs*/*/coefficient.dat under %s"
                            % case_dir)
    if len(hits) > 1:
        raise FoamReadError(
            "%d coefficient.dat files under %s (%s): a restart left more than one "
            "force history and the comparator will not choose between them"
            % (len(hits), case_dir, ", ".join(hits)))
    return hits[0]


def read_coefficient_dat(path):
    """Return dict(times, cols={name: ndarray}, path).  Column names come from
    the LAST `#` line, which OpenFOAM writes as the header row."""
    if not os.path.isfile(path):
        raise FoamReadError("no coefficient.dat at %s" % path)
    header, rows = None, []
    for line in open(path):
        if line.startswith("#"):
            header = line
            continue
        parts = line.split()
        if parts:
            rows.append(parts)
    if header is None:
        raise FoamReadError("%s: no `#` header line" % path)
    names = header.lstrip("#").split()
    if not names or names[0] != "Time":
        raise FoamReadError("%s: header does not begin with `Time`: %r" % (path, names[:3]))
    if not rows:
        raise FoamReadError("%s: header only, ZERO data rows" % path)
    ncol = len(names)
    bad = [i for i, r in enumerate(rows) if len(r) != ncol]
    if bad:
        raise FoamReadError("%s: %d rows do not carry %d columns (first at data row %d)"
                            % (path, len(bad), ncol, bad[0]))
    arr = np.array([[float(v) for v in r] for r in rows])
    return dict(times=arr[:, 0], cols={n: arr[:, i] for i, n in enumerate(names)},
                path=path, ncol=ncol, names=names)


def read_cl(case_dir):
    """THE GRADED READER.  Returns dict(t, cl, cd, times, cl_series, cd_series,
    path).  `cl` is `CL_aero` at the final time -- the number section 5.6 turns
    into `CL_total` and section 7.2/7.3 gate.  Plant 1 certifies THIS reader."""
    path = coefficient_dat_path(case_dir)
    d = read_coefficient_dat(path)
    for need in ("Cl", "Cd"):
        if need not in d["cols"]:
            raise FoamReadError("%s: no `%s` column (have %s)" % (path, need, d["names"]))
    i = int(np.argmax(d["times"]))
    return dict(t=float(d["times"][i]), cl=float(d["cols"]["Cl"][i]),
                cd=float(d["cols"]["Cd"][i]), times=d["times"],
                cl_series=d["cols"]["Cl"], cd_series=d["cols"]["Cd"], path=path)


def plant_into_coefficient_dat(src, dst, column, delta):
    """Copy `coefficient.dat` adding `delta` to `column` AT THE FINAL TIME,
    BY LINE INDEX (section 8.2 Plant 1: "perturbed by line index at the final
    time").  Returns (line_index, before, after).  Writes a real file."""
    lines = open(src).read().splitlines(keepends=True)
    header, data_idx = None, []
    for i, line in enumerate(lines):
        if line.startswith("#"):
            header = line
        elif line.split():
            data_idx.append(i)
    if header is None or not data_idx:
        raise FoamReadError("%s: no header or no data rows to plant into" % src)
    names = header.lstrip("#").split()
    if column not in names:
        raise FoamReadError("%s: no `%s` column to plant into" % (src, column))
    col = names.index(column)
    times = [float(lines[i].split()[0]) for i in data_idx]
    target = data_idx[int(np.argmax(times))]
    parts = lines[target].split()
    before = float(parts[col])
    after = before + delta
    parts[col] = "%.10e" % after
    lines[target] = "\t".join(parts) + "\n"
    with open(dst, "w") as fh:
        fh.write("".join(lines))
    return target, before, after


# ---------------------------------------------------------------------------
# surfaceFieldValue -- THE JET MASS-FLOW READER (Plant 2)
# ---------------------------------------------------------------------------
def jet_massflow_dat_path(case_dir, fo_name="jetMassFlow"):
    root = os.path.join(case_dir, "postProcessing", fo_name)
    if not os.path.isdir(root):
        raise FoamReadError("no postProcessing/%s under %s" % (fo_name, case_dir))
    hits = []
    for sub in sorted(os.listdir(root)):
        p = os.path.join(root, sub, "surfaceFieldValue.dat")
        if os.path.isfile(p):
            hits.append(p)
    if not hits:
        raise FoamReadError("no %s/*/surfaceFieldValue.dat under %s" % (fo_name, case_dir))
    if len(hits) > 1:
        raise FoamReadError("%d surfaceFieldValue.dat files under %s: the comparator "
                            "will not choose between them" % (len(hits), root))
    return hits[0]


def read_jet_sum_phi(case_dir, fo_name="jetMassFlow"):
    """THE GRADED READER for section 7.4's jet mass flow and for section 8.4's
    `area(jetSlot)` refusal.  Returns dict(t, sum_phi, area, faces, path).

    `phi` is VOLUMETRIC in incompressible OpenFOAM -- section 5.6 HAZARD 3 --
    so `sum_phi` is m3/s and is compared against `V_j h t_z` in m3/s.  The
    header `Area` is the independent `t_z` probe of section 5.6 item 3."""
    path = jet_massflow_dat_path(case_dir, fo_name)
    area, faces, times, vals = None, None, [], []
    for line in open(path):
        if line.startswith("#"):
            m = re.search(r"Area\s*:\s*(%s)" % _NUM, line)
            if m:
                area = float(m.group(1))
            m = re.search(r"Faces\s*:\s*(\d+)", line)
            if m:
                faces = int(m.group(1))
            continue
        parts = line.split()
        if len(parts) >= 2:
            times.append(float(parts[0]))
            vals.append(float(parts[1]))
    if not times:
        raise FoamReadError("%s: header only, ZERO data rows" % path)
    if area is None:
        raise FoamReadError("%s: no `# Area` header -- the t_z cross-check of "
                            "section 5.6 has no probe without it" % path)
    i = int(np.argmax(np.array(times)))
    return dict(t=times[i], sum_phi=vals[i], area=area, faces=faces, path=path,
                times=np.array(times), series=np.array(vals))


def plant_into_surface_field_value(src, dst, value):
    """Write `value` into the `sum(phi)` column at the FINAL time, by line
    index.  Real file on disk; read back through `read_jet_sum_phi`."""
    lines = open(src).read().splitlines(keepends=True)
    data_idx = [i for i, l in enumerate(lines) if not l.startswith("#") and l.split()]
    if not data_idx:
        raise FoamReadError("%s: no data rows to plant into" % src)
    times = [float(lines[i].split()[0]) for i in data_idx]
    target = data_idx[int(np.argmax(times))]
    parts = lines[target].split()
    before = float(parts[1])
    parts[1] = "%.10e" % value
    lines[target] = "\t".join(parts) + "\n"
    with open(dst, "w") as fh:
        fh.write("".join(lines))
    return target, before, value


# ---------------------------------------------------------------------------
# yPlus and fieldMinMax -- section 7.4 y+, section 5.5a blow-up guard
# ---------------------------------------------------------------------------
def read_yplus(case_dir, patch="airfoil"):
    root = os.path.join(case_dir, "postProcessing", "yPlus")
    if not os.path.isdir(root):
        raise FoamReadError("no postProcessing/yPlus under %s: `max(y+) <= 1` is a "
                            "gate and a gate whose quantity was never written is "
                            "unverifiable" % case_dir)
    rows = []
    for sub in sorted(os.listdir(root)):
        p = os.path.join(root, sub, "yPlus.dat")
        if not os.path.isfile(p):
            continue
        for line in open(p):
            if line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 5 and parts[1] == patch:
                rows.append((float(parts[0]), float(parts[2]), float(parts[3]),
                             float(parts[4]), p))
    if not rows:
        raise FoamReadError("no y+ data rows for patch `%s` under %s" % (patch, root))
    rows.sort(key=lambda r: r[0])
    t, ymin, ymax, yavg, p = rows[-1]
    return dict(t=t, min=ymin, max=ymax, avg=yavg, path=p, n_rows=len(rows))


def read_field_min_max(case_dir, field="mag(U)", fo_name="minMaxU"):
    root = os.path.join(case_dir, "postProcessing", fo_name)
    if not os.path.isdir(root):
        raise FoamReadError("no postProcessing/%s under %s" % (fo_name, case_dir))
    rows = []
    for sub in sorted(os.listdir(root)):
        p = os.path.join(root, sub, "fieldMinMax.dat")
        if not os.path.isfile(p):
            continue
        for line in open(p):
            if line.startswith("#"):
                continue
            m = re.match(r"\s*(%s)\s+(\S+)\s+(%s)\s+(\([^)]*\))\s+(%s)\s+(\([^)]*\))"
                         % (_NUM, _NUM, _NUM), line)
            if m and m.group(2) == field:
                rows.append((float(m.group(1)), float(m.group(3)), m.group(4),
                             float(m.group(5)), m.group(6), p))
    if not rows:
        raise FoamReadError("no `%s` rows under %s" % (field, root))
    rows.sort(key=lambda r: r[0])
    t, vmin, locmin, vmax, locmax, p = rows[-1]
    return dict(t=t, min=vmin, loc_min=locmin, max=vmax, loc_max=locmax, path=p)


# ---------------------------------------------------------------------------
# log.simpleFoam -- section 8.1 clauses 2, 3, 5 and section 5.5b continuity
# ---------------------------------------------------------------------------
CONVERGED_RE = re.compile(r"^SIMPLE solution converged in (\d+) iterations\s*$", re.M)
EXEC_RE = re.compile(r"^ExecutionTime = ", re.M)
TIME_RE = re.compile(r"^Time = (\S+)\s*$", re.M)
FATAL_RE = re.compile(r"FOAM FATAL|FOAM exiting|Floating point exception|"
                      r"signal \(|Segmentation fault|std::bad_alloc|"
                      r"Killed|Out of memory|MPI_ABORT", re.I)


def read_solver_log(path):
    """Parse the solver log ONCE and return every fact sections 8.1 and 5.5b
    read from it.  A log this cannot open is a refusal, never a default."""
    if not os.path.isfile(path):
        raise FoamReadError("no solver log at %s" % path)
    text = open(path, errors="replace").read()
    conv = [int(m.group(1)) for m in CONVERGED_RE.finditer(text)]
    times = TIME_RE.findall(text)
    blocks = TIME_RE.split(text)
    final_block = blocks[-1] if len(blocks) > 1 else text
    return dict(path=path, text=text, has_end=bool(re.search(r"^End\s*$", text, re.M)),
                converged=conv, n_exec=len(EXEC_RE.findall(text)),
                times=times, final_block=final_block,
                fatal=FATAL_RE.search(text).group(0) if FATAL_RE.search(text) else None,
                last_line=(text.rstrip().splitlines() or ["<empty>"])[-1])


def final_initial_residuals(log):
    """Section 8.1 clause 3a: "the final iteration's initial residuals for `p`,
    `Ux`, `Uy`, `k`, `omega`, read from the log".

    `p` is taken from the FIRST `Solving for p` of the final iteration.  With
    `nNonOrthogonalCorrectors 1` there are two pressure solves per iteration and
    `simpleControl::criteriaSatisfied()` tests the FIRST one; taking the last
    would read a corrector residual and silently pass a run the solver itself
    would not have called converged."""
    out = {}
    for name in ("Ux", "Uy", "p", "k", "omega"):
        m = re.search(r"Solving for %s, Initial residual = (%s)" % (re.escape(name), _NUM),
                      log["final_block"])
        out[name] = float(m.group(1)) if m else None
    return out


def final_continuity(log):
    """Section 5.5b: the GATED quantity is `sum local` at the FINAL iteration;
    `global` and `cumulative` are REPORTED and gated on nothing."""
    m = None
    for m in re.finditer(r"time step continuity errors : sum local = (%s), global = (%s), "
                         r"cumulative = (%s)" % (_NUM, _NUM, _NUM), log["final_block"]):
        pass
    if m is None:
        return None
    return dict(sum_local=float(m.group(1)), glob=float(m.group(2)),
                cumulative=float(m.group(3)))


# ---------------------------------------------------------------------------
# RUN_STATUS -- section 8.1 clause 1, section 9.2/9.3
# ---------------------------------------------------------------------------
def run_status_path(case_dir, case_id):
    """The REGISTERED path, section 9.3: `artefacts/RUN_STATUS.<case_id>.txt`,
    "which is neither of those two paths and which the runner never touches".
    `STATUS.<case_id>` is NEVER read -- section 9.3 forbids it in terms."""
    return os.path.join(case_dir, "artefacts", "RUN_STATUS.%s.txt" % case_id)


def read_run_status(case_dir, case_id):
    """Parse the wrapper's `key=value` record (section 9.2).  `solver_rc` is
    the SOLVER's rc captured inside the wrapper."""
    path = run_status_path(case_dir, case_id)
    if not os.path.isfile(path):
        raise FoamReadError(
            "no RUN_STATUS at the registered path %s. Section 9.3 registers this "
            "path and this path only; `STATUS.%s` is the queue runner's own "
            "infrastructure record and section 9.3 forbids reading rule 4's rc "
            "from it." % (path, case_id))
    out = {}
    for line in open(path):
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return dict(fields=out, path=path)


# ---------------------------------------------------------------------------
# TIME DIRECTORIES -- N_stop, and the pre-launch guard
# ---------------------------------------------------------------------------
def numeric_time_dirs(case_dir):
    out = []
    for d in sorted(os.listdir(case_dir)):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and os.path.isdir(os.path.join(case_dir, d)):
            out.append(d)
    return sorted(out, key=float)


def n_stop(case_dir):
    """`N_stop` = the name of the LAST time directory written (section 8.1
    clause 3), excluding `0` which is the initial condition."""
    dirs = [d for d in numeric_time_dirs(case_dir) if float(d) != 0.0]
    if not dirs:
        return None, []
    return dirs[-1], dirs


# ---------------------------------------------------------------------------
# THE THEORY DIFFERENCE CHANNEL -- Plant 3
# ---------------------------------------------------------------------------
def theory_rel_diff(cl_total, cl_theory):
    """Section 7.3's graded quantity: `|CL_total - CL_theory| / CL_theory`.
    Plant 3 certifies this channel; the disk-routed limb certifies
    `read_cl` -> `cl_total` -> this function end to end."""
    if cl_theory == 0.0:
        raise FoamReadError("theory_rel_diff: CL_theory is zero; the relative "
                            "difference is undefined and is NOT reported as 0.0")
    return abs(cl_total - cl_theory) / cl_theory


def cl_total(cl_aero, c_mu_jet, alpha_deg, tau=math.pi / 6.0):
    """Section 5.6 / section 1.6: `CL_total = CL_aero + C_mu_jet sin(tau + alpha)`
    in the AIRFOIL FRAME registered by section 1.6a."""
    return cl_aero + c_mu_jet * math.sin(tau + math.radians(alpha_deg))


# ---------------------------------------------------------------------------
# BYTE-LEVEL COPY -- every mutation limb runs on one of these
# ---------------------------------------------------------------------------
def byte_copy_case(src, dst):
    """`shutil.copytree` with metadata: a BYTE-LEVEL copy, section 8.2's own
    requirement.  mtimes are preserved so the age guard is copied faithfully
    rather than reset by the act of copying."""
    if os.path.exists(dst):
        raise FoamReadError("refusing to copy over an existing path %s" % dst)
    shutil.copytree(src, dst, symlinks=True)
    for root, dirs, files in os.walk(src):
        rel = os.path.relpath(root, src)
        for name in files + dirs:
            s = os.path.join(root, name)
            d = os.path.join(dst, rel, name) if rel != "." else os.path.join(dst, name)
            if os.path.exists(d) and not os.path.islink(d):
                st = os.stat(s)
                os.utime(d, (st.st_atime, st.st_mtime))
    return dst
