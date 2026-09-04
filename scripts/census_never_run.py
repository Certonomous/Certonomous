#!/usr/bin/env python3
"""census_never_run.py -- classify every OpenFOAM case root in cfd territory by
what its ARTIFACTS ON DISK prove about whether a solver ever ran for it.

WHY THIS EXISTS
---------------
Sanaa, 2026-09-04 (etc/sessions/2026-09-04T0050Z_sanaa_all_cases_mandatory.md):
every assigned case is mandatory to completion, "especially the never run", and
the only exemption is a case genuinely unrunnable with OpenFOAM.  An accurate
never-run list is therefore the INPUT to a mandatory work order, and a false
negative here means a case Sanaa ordered run is silently never run.

A previous lane attempted this with stem-pairing (matching case names against
run-directory names) and reported its own defect: stem-pairing has false
negatives.  This classifier does not name-match to decide whether a case ran.
It reads the filesystem.

CLAUDE.md rule 3 (planted-zero control): "this case never ran" is a ZERO,
asserted at scale.  A zero from a reader not shown able to see a non-zero is not
evidence.  So --selftest plants a fixture containing a known member of every
class -- including a case that ran but whose only evidence is decomposed into
processor* directories, and a case whose verdict exists only in
verification/campaign/ -- and the census REFUSES TO RUN (exit 2) unless the
control passes.  Comparators in this lab refuse; they do not degrade.

CLAUDE.md / `gitignored is not filed`: solver logs under verification/runs are
gitignored (.gitignore:260 `verification/runs/*_runs/**/log.*`).  Any check that
asks git is blind to exactly the evidence it needs.  This reads the disk.

===========================================================================
THE PREDICATES.  Every count this script prints is the size of one of these
sets.  A count quoted without its predicate is not a result.
===========================================================================

CENSUS UNIT -- "case root": a directory D such that D/system/controlDict is a
  regular file (a CONCRETE, runnable OpenFOAM case), or D/system/ holds a
  controlDict*.template (a case DEFINITION awaiting instantiation).  This is a
  measured property of the tree, not a name.

EVIDENCE, all measured on D:
  E_log      >=1 log file at D (or D/logs/) containing a line beginning
             "ExecutionTime = ".  Calibrated on this corpus: blockMesh,
             checkMesh, writeCellCentres, decomposePar and reconstructPar logs
             score 0; rhoCentralFoam scores 1000 in the same case directory
             (verification/runs/F19_SOD_runs/coarse/).  This is the time-loop
             signature and it is what "a solver executed" means here.
  E_time     >=1 child directory of D whose name parses as a float > 0 and
             which contains >=1 regular file.
  E_ptime    same, but inside D/processor*/ -- a decomposed run that was never
             reconstructed leaves NOTHING at D level.  This is the non-obvious
             location the control plants for.
  E_mesh     D/constant/polyMesh/{points,points.gz,owner} exists, or a log at D
             attributes to a mesh utility.
  E_end      >=1 solver log at D containing a line beginning "End".
  RC         D/RC.txt contents, if present.

BINARY ATTRIBUTION: from the log's own "Exec   : <path>/<binary>" banner when
  present; otherwise from the filename stem (log.<binary>[.gz][.suffix]).  The
  fallback is NOT cosmetic: 20 logs in this territory carry ExecutionTime lines
  and NO Exec banner (e.g. verification/runs/F12_runs/coarse_workshop_M0.734_a2.79/
  log.rhoSimpleFoam, 179 ExecutionTime lines, no banner).  A classifier keying
  only on the banner would call all 20 of those cases never-run.

REFUSAL CLAUSE: if a log shows a time loop but its binary is in neither
  SOLVERS, INIT_ONLY_BINS nor UTILITIES, the script EXITS 2 rather than guess.
  An unknown solver silently filed as a utility is the exact false negative
  this census exists to prevent.

CLASSES (mutually exclusive, evaluated in this order):
  TEMPLATE_ONLY   no system/controlDict; only a controlDict*.template.  A case
                  DEFINITION.  Not evidence of anything having run, and not
                  itself a runnable unit -- its instances are counted elsewhere.
  RAN             E_log from a SOLVER binary, OR E_time, OR E_ptime.
                  Sub-labelled COMPLETE when E_end holds and RC is absent or 0.
  INIT_ONLY       E_log holds but every time-looping log attributes to
                  INIT_ONLY_BINS (potentialFoam), and no E_time/E_ptime.
                  Potential-flow initialisation is not the case's solve.
  MESH_ONLY       no solve evidence, but E_mesh.
  NEVER_RUN       no solve evidence and no mesh evidence.

CANNOT_RUN_WITH_OPENFOAM is an ORTHOGONAL, MEASURED overlay, never a class
  assigned from difficulty: system/controlDict names `application <X>;` and X is
  not a file in any known OpenFOAM bin directory.  The missing capability is
  NAMED in the output.  Absence of this flag is NOT proof a case is runnable --
  it proves only that the solver binary its controlDict names exists.

GRADED overlay: a file under verification/campaign/ (or beside the case) whose
  NAME contains the case's family key AND whose CONTENT carries a token from the
  fixed verdict vocabulary.  This overlay IS name-linked and is the weakest
  claim in this script; it is reported with its artifact path so it can be
  checked, and "no verdict found" resolves conservatively to UNGRADED (which
  costs work, never a skipped case).

Usage:
  python3 scripts/census_never_run.py --selftest      # planted control only
  python3 scripts/census_never_run.py --census        # control, then census
  python3 scripts/census_never_run.py --census --json out.json
"""

import argparse
import gzip
import json
import os
import re
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------- territory --
# cfd territory per CLAUDE.md TEAM ROSTER: cases/ except closure and dafoam;
# verification/runs/ except the three heat-transfer trees; models/.
CASES_EXCLUDE = {"RANS_LES_closure_models", "dafoam"}
RUNS_EXCLUDE = {"T-family", "F14-cooling-ladder", "THERMAL_K0_runs"}

# ------------------------------------------------- binary partition (v1) -----
# Measured: every distinct `Exec` banner binary appearing in this territory's
# 2,730 log files was enumerated before this list was written.  Adding a name
# here is a deliberate act; an unlisted time-looping binary makes the script
# REFUSE rather than be silently misfiled.
SOLVERS = {
    "simpleFoam", "rhoCentralFoam", "interFoam", "rhoSimpleFoam", "pimpleFoam",
    "icoFoam", "buoyantSimpleFoam", "buoyantBoussinesqSimpleFoam",
    "interPhaseChangeFoam", "scalarTransportFoam", "laplacianFoam",
    "rhoCentralFoamBounded", "rhoCentralFoamBoundedDiag",
    "rhoCentralFoamInletUpwindDiag", "kCorrectiveFrozenFoam",
    "sonicFoam", "rhoPimpleFoam", "pisoFoam", "chtMultiRegionFoam",
    "chtMultiRegionSimpleFoam", "overSimpleFoam", "DPMFoam",
}
# Ran, produced ExecutionTime output, but is not the case's physics solve.
INIT_ONLY_BINS = {"potentialFoam"}
UTILITIES = {
    "checkMesh", "blockMesh", "postProcess", "decomposePar", "topoSet",
    "reconstructPar", "reconstructParMesh", "plot3dToFoam", "setFields",
    "snappyHexMesh", "surfaceFeatureExtract", "autoPatch", "createPatch",
    "transformPoints", "setExprFields", "mapFields", "renumberMesh",
    "writeCellCentres", "writeCellVolumes", "foamDictionary", "surfaceCheck",
    "extrudeMesh", "mergeMeshes", "splitMeshRegions", "createBaffles",
    "viewFactorsGen", "moveDynamicMesh", "checkMesh.build", "foamToVTK",
    "surfaceTransformPoints", "surfaceMeshTriangulate", "particleTracks",
    "flattenMesh", "stitchMesh", "refineMesh", "polyDualMesh", "attachMesh",
    "changeDictionary", "setAlphaField", "mirrorMesh", "collapseEdges",
    "checkSurfaceMesh", "ideasUnvToFoam", "fluentMeshToFoam", "gmshToFoam",
    "star4ToFoam", "cfx4ToFoam", "foamMeshToFluent", "zipUpMesh",
}
MESH_BINS = {
    "blockMesh", "snappyHexMesh", "checkMesh", "plot3dToFoam", "extrudeMesh",
    "ideasUnvToFoam", "fluentMeshToFoam", "gmshToFoam", "refineMesh",
    "renumberMesh", "mergeMeshes", "createPatch", "topoSet", "autoPatch",
    "splitMeshRegions", "transformPoints", "reconstructParMesh", "flattenMesh",
    "stitchMesh", "polyDualMesh", "attachMesh", "mirrorMesh", "collapseEdges",
    "zipUpMesh",
}

FOAM_BIN_DIRS = [
    "/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin",
    "/home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin",
]

VERDICT_RE = re.compile(r"\b(PASS|GATE REACHED|GATE FAIL|NOT A RESULT|BLOCKED|PENDING)\b")

EXEC_TIME_PREFIX = "ExecutionTime = "
PRUNE_DIRS = {
    "polyMesh", "postProcessing", "__pycache__", ".git", "VTK", "dynamicCode",
    "triSurface", "extendedFeatureEdgeMesh", "sets", "uniform", "lagrangian",
}

# ------------------------------------------------------------------ helpers --


def _is_time_name(name):
    """True if `name` parses as an OpenFOAM time-directory name with value > 0."""
    try:
        v = float(name)
    except (TypeError, ValueError):
        return False
    return v > 0.0


def _dir_has_regular_file(path, cap=4000):
    """True if `path` contains at least one regular file, at any depth."""
    seen = 0
    for dp, _dn, fn in os.walk(path):
        for f in fn:
            if os.path.isfile(os.path.join(dp, f)):
                return True
            seen += 1
            if seen > cap:
                return False
        seen += len(fn)
        if seen > cap:
            return False
    return False


def _read_text(path, limit=8 * 1024 * 1024):
    opener = gzip.open if path.endswith(".gz") else open
    try:
        with opener(path, "rt", errors="replace") as fh:
            return fh.read(limit)
    except Exception:
        return ""


def _attribute_binary(path, text):
    """Binary that produced this log: Exec banner first, filename stem second."""
    for line in text.split("\n", 60)[:60]:
        if line.startswith("Exec"):
            if ":" in line:
                tail = line.split(":", 1)[1].strip()
                if tail:
                    return os.path.basename(tail.split()[0]), "banner"
            break
    name = os.path.basename(path)
    if name.endswith(".gz"):
        name = name[:-3]
    if name.startswith("log."):
        stem = name[4:]
    elif name.endswith(".log"):
        stem = name[:-4]
    else:
        stem = name
    # strip trailing qualifiers: log.simpleFoam.monitor, log.solve.legA, log.checkMesh.fluid
    stem = stem.split(".")[0]
    return stem, "filename"


def _log_files(case_root):
    out = []
    for d in (case_root, os.path.join(case_root, "logs")):
        if not os.path.isdir(d):
            continue
        try:
            entries = os.listdir(d)
        except OSError:
            continue
        for f in entries:
            p = os.path.join(d, f)
            if not os.path.isfile(p):
                continue
            if f.startswith("log.") or f.endswith(".log") or f.endswith(".log.gz"):
                out.append(p)
    return sorted(out)


def _foam_binary_exists(name):
    for d in FOAM_BIN_DIRS:
        if os.path.isfile(os.path.join(d, name)):
            return True
    return bool(shutil.which(name))


def _controldict_application(case_root):
    p = os.path.join(case_root, "system", "controlDict")
    if not os.path.isfile(p):
        return None
    try:
        txt = open(p, errors="replace").read(200000)
    except OSError:
        return None
    m = re.search(r"^\s*application\s+([A-Za-z0-9_]+)\s*;", txt, re.M)
    return m.group(1) if m else None


# ------------------------------------------------------------- discovery -----


def discover_case_roots(territory_roots):
    """Every case root under the given roots.  See PREDICATES: CENSUS UNIT."""
    found = []
    for root in territory_roots:
        if not os.path.isdir(root):
            continue
        for dp, dn, _fn in os.walk(root):
            dn[:] = [
                d for d in dn
                if d not in PRUNE_DIRS
                and not _is_time_name(d)
                and not d.startswith("processor")
            ]
            sysd = os.path.join(dp, "system")
            if not os.path.isdir(sysd):
                continue
            try:
                sysfiles = os.listdir(sysd)
            except OSError:
                continue
            has_cd = "controlDict" in sysfiles and os.path.isfile(os.path.join(sysd, "controlDict"))
            has_tpl = any(f.startswith("controlDict") and f.endswith(".template") for f in sysfiles)
            if has_cd or has_tpl:
                found.append((dp, has_cd, has_tpl))
    return sorted(found)


# ------------------------------------------------------------ classifier -----


class Refusal(Exception):
    """An unknown time-looping binary.  Refuse, never degrade."""


def classify_case(case_root, has_cd, has_tpl):
    ev = {
        "case_root": case_root,
        "has_controlDict": has_cd,
        "has_template": has_tpl,
        "time_dirs": [],
        "processor_time_dirs": [],
        "solver_logs": [],
        "init_logs": [],
        "mesh_logs": [],
        "end_line": False,
        "rc": None,
        "mesh_points": False,
        "application": None,
        "missing_binary": None,
    }

    try:
        children = os.listdir(case_root)
    except OSError:
        children = []

    # E_time
    for c in children:
        p = os.path.join(case_root, c)
        if os.path.isdir(p) and _is_time_name(c) and _dir_has_regular_file(p):
            ev["time_dirs"].append(c)
    # E_ptime -- decomposed run never reconstructed
    for c in children:
        if not c.startswith("processor"):
            continue
        p = os.path.join(case_root, c)
        if not os.path.isdir(p):
            continue
        try:
            for t in os.listdir(p):
                tp = os.path.join(p, t)
                if os.path.isdir(tp) and _is_time_name(t) and _dir_has_regular_file(tp):
                    ev["processor_time_dirs"].append(f"{c}/{t}")
        except OSError:
            pass

    # E_mesh (points)
    pmd = os.path.join(case_root, "constant", "polyMesh")
    for f in ("points", "points.gz", "owner", "owner.gz"):
        if os.path.isfile(os.path.join(pmd, f)):
            ev["mesh_points"] = True
            break

    # logs
    for lp in _log_files(case_root):
        text = _read_text(lp)
        if not text:
            continue
        nexec = 0
        has_end = False
        for line in text.split("\n"):
            if line.startswith(EXEC_TIME_PREFIX):
                nexec += 1
            elif line.startswith("End"):
                has_end = True
        binary, how = _attribute_binary(lp, text)
        if binary in MESH_BINS:
            ev["mesh_logs"].append({"path": lp, "binary": binary})
        if nexec == 0:
            continue
        rec = {"path": lp, "binary": binary, "attribution": how,
               "execution_time_lines": nexec, "end_line": has_end}
        if binary in SOLVERS:
            ev["solver_logs"].append(rec)
            if has_end:
                ev["end_line"] = True
        elif binary in INIT_ONLY_BINS:
            ev["init_logs"].append(rec)
        elif binary in UTILITIES:
            pass
        else:
            raise Refusal(
                f"unknown time-looping binary {binary!r} "
                f"({nexec} ExecutionTime lines, attributed by {how}) in {lp}. "
                "Add it to SOLVERS, INIT_ONLY_BINS or UTILITIES in "
                "scripts/census_never_run.py -- refusing rather than guessing."
            )

    rcp = os.path.join(case_root, "RC.txt")
    if os.path.isfile(rcp):
        ev["rc"] = _read_text(rcp, 256).strip()

    # CANNOT_RUN overlay -- measured, never inferred from difficulty
    # `application none;` is a LEGITIMATE OpenFOAM value -- a mesh-only or
    # utility case declaring that no solver is set.  It is not a capability
    # gap, and calling it one would hand out a false exemption from the one
    # exemption class Sanaa allows.  Measured, never inferred.
    app = _controldict_application(case_root)
    ev["application"] = app
    if app and app.lower() != "none" and not _foam_binary_exists(app):
        ev["missing_binary"] = app

    # ---- class assignment, in order ----
    solve_evidence = bool(ev["solver_logs"] or ev["time_dirs"] or ev["processor_time_dirs"])
    mesh_evidence = bool(ev["mesh_points"] or ev["mesh_logs"])

    if not has_cd and has_tpl:
        cls = "TEMPLATE_ONLY"
    elif solve_evidence:
        rc_ok = ev["rc"] in (None, "", "0")
        cls = "RAN_COMPLETE" if (ev["end_line"] and rc_ok) else "RAN_INCOMPLETE"
    elif ev["init_logs"]:
        cls = "INIT_ONLY"
    elif mesh_evidence:
        cls = "MESH_ONLY"
    else:
        cls = "NEVER_RUN"

    ev["klass"] = cls
    ev["evidence_path"] = _pick_evidence_path(ev, cls)
    return ev


def _pick_evidence_path(ev, cls):
    """The single artifact a reader should open to check this classification."""
    if cls.startswith("RAN"):
        if ev["solver_logs"]:
            return ev["solver_logs"][0]["path"]
        if ev["time_dirs"]:
            return os.path.join(ev["case_root"], sorted(ev["time_dirs"])[0])
        if ev["processor_time_dirs"]:
            return os.path.join(ev["case_root"], sorted(ev["processor_time_dirs"])[0])
    if cls == "INIT_ONLY":
        return ev["init_logs"][0]["path"]
    if cls == "MESH_ONLY":
        if ev["mesh_points"]:
            return os.path.join(ev["case_root"], "constant", "polyMesh")
        return ev["mesh_logs"][0]["path"]
    if cls == "TEMPLATE_ONLY":
        return os.path.join(ev["case_root"], "system")
    return os.path.join(ev["case_root"], "system", "controlDict")


# --------------------------------------------------------------- verdicts ----


def family_key(case_root, repo=REPO):
    """Family a case root belongs to: the campaign directory it sits under,
    with a trailing _runs/_work/_run stripped.

    NOTE ON RELIABILITY.  This is NAME-DERIVED and is a navigation aid only.
    It cannot be trusted to PAIR a definition under cases/ with its outputs
    under verification/runs/ -- cases/F19_SOD does pair with
    verification/runs/F19_SOD_runs, but cases/F17_kovasznay does NOT pair with
    verification/runs/F17_runs.  That is precisely the stem-pairing false
    negative a previous lane reported.  Nothing in this script's never-run
    classification depends on it; the class of a case root is decided by that
    root's own artifacts alone.
    """
    rel = os.path.relpath(case_root, repo)
    parts = rel.split(os.sep)
    if parts[0] == "verification" and len(parts) > 2:
        key = parts[2]          # verification/runs/<CAMPAIGN>/...
    elif len(parts) > 1:
        key = parts[1]          # cases/<CAMPAIGN>/... , models/<CAMPAIGN>/...
    else:
        return parts[0]
    for suf in ("_runs", "_work", "_run"):
        if key.endswith(suf):
            key = key[: -len(suf)]
            break
    return key


def discover_orphan_run_dirs(territory_roots, case_roots):
    """SECOND CENSUS UNIT -- a directory holding solver evidence but NO
    system/controlDict.

    Measured on this tree: verification/runs/MODEL_FORM_runs/B_re1p2e7_kEpsilon
    holds log.simpleFoam.gz with 154 ExecutionTime lines, log.blockMesh,
    log.checkMesh and postProcessing/ -- and no system/ or constant/ at all.
    The case was run and then pruned to save disk.  A census keyed only on
    system/controlDict does not see it, and MODEL_FORM would be absent from the
    roll-up entirely rather than shown as run.

    This unit cannot create a false NEVER_RUN (everything it finds RAN by
    construction), but without it the census UNDERCOUNTS what has been run and
    silently omits whole campaigns.
    """
    known = set(case_roots)
    orphans = []
    for root in territory_roots:
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in PRUNE_DIRS and not _is_time_name(d)
                     and not d.startswith("processor")]
            if dp in known or os.path.isdir(os.path.join(dp, "system")):
                continue
            if any(os.path.dirname(dp) == k or dp.startswith(k + os.sep) for k in known):
                continue
            logs = []
            for f in fn:
                if not (f.startswith("log.") or f.endswith(".log")
                        or f.endswith(".log.gz")):
                    continue
                p = os.path.join(dp, f)
                text = _read_text(p)
                nexec = sum(1 for ln in text.split("\n")
                            if ln.startswith(EXEC_TIME_PREFIX))
                if nexec == 0:
                    continue
                binary, how = _attribute_binary(p, text)
                if binary in SOLVERS:
                    logs.append({"path": p, "binary": binary,
                                 "execution_time_lines": nexec})
                elif binary in INIT_ONLY_BINS or binary in UTILITIES:
                    continue
                else:
                    raise Refusal(
                        f"unknown time-looping binary {binary!r} in orphan dir {p}"
                    )
            if logs:
                orphans.append({"case_root": dp, "klass": "RAN_LOGS_ONLY",
                                "solver_logs": logs, "has_controlDict": False,
                                "has_template": False, "missing_binary": None,
                                "application": None,
                                "evidence_path": logs[0]["path"]})
    return orphans


def build_verdict_index(campaign_dirs):
    """{lowercased filename: (path, [verdict tokens])} for files carrying a
    verdict token.  Name-linked; the weakest claim in this script."""
    idx = []
    for d in campaign_dirs:
        if not os.path.isdir(d):
            continue
        for dp, dn, fn in os.walk(d):
            dn[:] = [x for x in dn if x not in PRUNE_DIRS]
            for f in fn:
                if not f.endswith((".md", ".json", ".txt")):
                    continue
                p = os.path.join(dp, f)
                txt = _read_text(p, 2 * 1024 * 1024)
                toks = sorted(set(VERDICT_RE.findall(txt)))
                if toks:
                    idx.append((f.lower(), p, toks))
    return idx


def find_verdict(fkey, verdict_index):
    """Family key must appear as a delimited TOKEN in the filename, not as a
    bare substring: plain `k in name` makes family F1 match F17_KV40_RESULTS.md
    and silently mark F1 graded off F17's verdict.  Delimiters are the filename
    edges and any non-alphanumeric character."""
    k = re.escape(fkey.lower())
    pat = re.compile(r"(?:^|[^0-9a-z])" + k + r"(?:$|[^0-9a-z])")
    hits = [(p, t) for (name, p, t) in verdict_index if pat.search(name)]
    if not hits:
        return None
    hits.sort(key=lambda x: (0 if "result" in os.path.basename(x[0]).lower()
                             or "grading" in os.path.basename(x[0]).lower() else 1,
                             os.path.basename(x[0])))
    return hits[0]


# ------------------------------------------------------------- self-test -----

_SOLVER_LOG = """/*---------------------------------------------------------------------------*\\
| =========                 |                                                 |
\\*---------------------------------------------------------------------------*/
Build  : v2606
Exec   : /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/simpleFoam -case /x
Time = 1
smoothSolver:  Solving for Ux, Initial residual = 1, Final residual = 1e-06
ExecutionTime = 0.1 s  ClockTime = 0 s

Time = 2
ExecutionTime = 0.2 s  ClockTime = 0 s

End
"""

# Same solver output with the OpenFOAM banner stripped -- the shape that made 20
# real logs in this territory invisible to a banner-only reader.
_SOLVER_LOG_NO_BANNER = """Time = 1
smoothSolver:  Solving for Ux, Initial residual = 1, Final residual = 1e-06
ExecutionTime = 0.1 s  ClockTime = 0 s
Time = 2
ExecutionTime = 0.2 s  ClockTime = 0 s
End
"""

_MESH_LOG = """Build  : v2606
Exec   : /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/blockMesh -case /x
Creating block mesh from "system/blockMeshDict"
Mesh Information
End
"""

_CHECKMESH_LOG = """Build  : v2606
Exec   : /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/checkMesh -case /x
Time = 0
Mesh OK.
End
"""

_POTENTIAL_LOG = """Build  : v2606
Exec   : /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/potentialFoam -case /x
Calculating potential flow
GAMG:  Solving for p, Initial residual = 1, Final residual = 1e-07
ExecutionTime = 0.4 s  ClockTime = 1 s
End
"""

_UNKNOWN_SOLVER_LOG = """Build  : v2606
Exec   : /usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/quantumFoam -case /x
Time = 1
ExecutionTime = 0.1 s  ClockTime = 0 s
End
"""


def _w(path, text=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def _mkcase(root, application="simpleFoam", template=False):
    if template:
        _w(os.path.join(root, "system", "controlDict.template"),
           "application     $APP;\n")
    else:
        _w(os.path.join(root, "system", "controlDict"),
           f"application     {application};\nstartTime 0;\nendTime 100;\n")
    _w(os.path.join(root, "system", "fvSchemes"), "")
    _w(os.path.join(root, "0", "U"), "internalField uniform (0 0 0);\n")
    return root


def build_fixture(base):
    """Plant one KNOWN member of every class, including two the brief names
    explicitly: a case that ran but whose artifacts sit in a non-obvious place,
    and a case whose verdict lives only in verification/campaign/."""
    cases = os.path.join(base, "cases")
    runs = os.path.join(base, "verification", "runs")
    camp = os.path.join(base, "verification", "campaign")
    expect = {}

    # 1. NEVER RUN -- controlDict and 0/, nothing else.
    r = _mkcase(os.path.join(cases, "CTRLNEVER_case"))
    expect[r] = "NEVER_RUN"

    # 2. MESH_ONLY -- mesh built, no solve.
    r = _mkcase(os.path.join(runs, "CTRLMESH_runs", "L1"))
    _w(os.path.join(r, "constant", "polyMesh", "points"), "8\n(\n)\n")
    _w(os.path.join(r, "log.blockMesh"), _MESH_LOG)
    _w(os.path.join(r, "log.checkMesh"), _CHECKMESH_LOG)
    expect[r] = "MESH_ONLY"

    # 3. RAN_COMPLETE, ungraded -- ordinary solver log + written time dir.
    r = _mkcase(os.path.join(runs, "CTRLRAN_runs", "L1"))
    _w(os.path.join(r, "constant", "polyMesh", "points"), "8\n(\n)\n")
    _w(os.path.join(r, "log.blockMesh"), _MESH_LOG)
    _w(os.path.join(r, "log.simpleFoam"), _SOLVER_LOG)
    _w(os.path.join(r, "100", "U"), "internalField uniform (1 0 0);\n")
    _w(os.path.join(r, "RC.txt"), "0\n")
    expect[r] = "RAN_COMPLETE"

    # 4. RAN, NON-OBVIOUS LOCATION -- log banner stripped, generic filename,
    #    gzipped, and the ONLY field data is inside processor*/ (never
    #    reconstructed).  Nothing at case level says "ran".
    r = _mkcase(os.path.join(runs, "CTRLHIDDEN_runs", "deep", "nest", "case"))
    _w(os.path.join(r, "constant", "polyMesh", "points"), "8\n(\n)\n")
    with gzip.open(os.path.join(r, "log.simpleFoam.gz"), "wt") as fh:
        fh.write(_SOLVER_LOG_NO_BANNER)
    _w(os.path.join(r, "processor0", "50", "U"), "internalField uniform (1 0 0);\n")
    _w(os.path.join(r, "processor1", "50", "U"), "internalField uniform (1 0 0);\n")
    expect[r] = "RAN_COMPLETE"

    # 5. RAN but graded ONLY in verification/campaign/ -- no marker beside it.
    r = _mkcase(os.path.join(runs, "CTRLGRADED_runs", "L1"))
    _w(os.path.join(r, "log.simpleFoam"), _SOLVER_LOG)
    _w(os.path.join(r, "100", "U"), "internalField uniform (1 0 0);\n")
    _w(os.path.join(camp, "CTRLGRADED_RESULTS.md"),
       "# CTRLGRADED results\n\nVerdict: GATE FAIL at the pre-registered band.\n")
    expect[r] = "RAN_COMPLETE"

    # 6. INIT_ONLY -- potentialFoam ran, the case solver did not.
    r = _mkcase(os.path.join(runs, "CTRLINIT_runs", "L1"))
    _w(os.path.join(r, "constant", "polyMesh", "points"), "8\n(\n)\n")
    _w(os.path.join(r, "log.potentialFoam"), _POTENTIAL_LOG)
    expect[r] = "INIT_ONLY"

    # 7. TEMPLATE_ONLY -- a case definition, not an instance.
    r = _mkcase(os.path.join(cases, "CTRLTPL_case"), template=True)
    expect[r] = "TEMPLATE_ONLY"

    # 8. RAN_INCOMPLETE -- solver ran, no End line, rc non-zero.
    r = _mkcase(os.path.join(runs, "CTRLCRASH_runs", "L1"))
    _w(os.path.join(r, "log.simpleFoam"),
       _SOLVER_LOG.replace("\nEnd\n", "\n#0 Foam::error::printStack\n"))
    _w(os.path.join(r, "RC.txt"), "139\n")
    expect[r] = "RAN_INCOMPLETE"

    # 9. CANNOT_RUN overlay -- controlDict names a solver with no binary.
    r = _mkcase(os.path.join(cases, "CTRLNOSOLVER_case"), application="forteCombustionFoam")
    expect[r] = "NEVER_RUN"

    # 10. `application none;` -- a legitimate mesh-only declaration.  Must NOT
    #     be reported as a missing capability.
    r = _mkcase(os.path.join(cases, "CTRLAPPNONE_case"), application="none")
    expect[r] = "NEVER_RUN"

    # 11. PRUNED case -- it RAN, then system/ and constant/ were deleted.  The
    #     shape of verification/runs/MODEL_FORM_runs/*.  Invisible to a census
    #     keyed on system/controlDict; the orphan pass must catch it.
    r = os.path.join(runs, "CTRLPRUNED_runs", "L1")
    _w(os.path.join(r, "log.simpleFoam"), _SOLVER_LOG)
    _w(os.path.join(r, "log.blockMesh"), _MESH_LOG)
    _w(os.path.join(r, "record.json"), "{}\n")

    # 12. EMPTY run dir -- neither case root nor solver evidence.
    os.makedirs(os.path.join(runs, "CTRLEMPTY_runs", "L1"), exist_ok=True)

    return expect, camp


def selftest(verbose=True):
    """Plant the control, read it back, and PROVE the reader sees a non-zero.
    Returns True only if every planted case is labelled exactly right."""
    base = tempfile.mkdtemp(prefix="census_ctrl_")
    rows = []
    ok = True
    try:
        expect, camp = build_fixture(base)
        roots = [os.path.join(base, "cases"),
                 os.path.join(base, "verification", "runs")]
        found = discover_case_roots(roots)
        found_map = {}
        for cr, has_cd, has_tpl in found:
            found_map[cr] = classify_case(cr, has_cd, has_tpl)

        # --- discovery control: every planted case root must be FOUND ---
        for cr in expect:
            if cr not in found_map:
                rows.append(("DISCOVERY", os.path.relpath(cr, base), expect[cr],
                             "NOT DISCOVERED", "FAIL"))
                ok = False

        # --- class control ---
        for cr, want in expect.items():
            if cr not in found_map:
                continue
            got = found_map[cr]["klass"]
            good = got == want
            ok &= good
            rows.append(("CLASS", os.path.relpath(cr, base), want, got,
                         "PASS" if good else "FAIL"))

        # --- non-zero control: the reader must SEE each class, not just miss ---
        seen = {v["klass"] for v in found_map.values()}
        for want in sorted(set(expect.values())):
            good = want in seen
            ok &= good
            rows.append(("NONZERO", f"class {want} observed at least once",
                         ">=1", "yes" if good else "NONE", "PASS" if good else "FAIL"))

        # --- CANNOT_RUN overlay control ---
        cr = os.path.join(base, "cases", "CTRLNOSOLVER_case")
        got = found_map.get(cr, {}).get("missing_binary")
        good = got == "forteCombustionFoam"
        ok &= good
        rows.append(("CANNOT_RUN", "CTRLNOSOLVER_case missing binary",
                     "forteCombustionFoam", str(got), "PASS" if good else "FAIL"))
        # and the negative half: a case naming a solver that DOES exist must not flag
        cr = os.path.join(base, "verification", "runs", "CTRLRAN_runs", "L1")
        got = found_map.get(cr, {}).get("missing_binary")
        good = got is None
        ok &= good
        rows.append(("CANNOT_RUN", "CTRLRAN/L1 (simpleFoam exists) must NOT flag",
                     "None", str(got), "PASS" if good else "FAIL"))
        # `application none;` is legitimate, not a capability gap
        cr = os.path.join(base, "cases", "CTRLAPPNONE_case")
        got = found_map.get(cr, {}).get("missing_binary")
        good = got is None
        ok &= good
        rows.append(("CANNOT_RUN", "'application none;' must NOT flag as missing",
                     "None", str(got), "PASS" if good else "FAIL"))

        # --- verdict-in-campaign-only control ---
        vidx = build_verdict_index([camp])
        v = find_verdict("CTRLGRADED", vidx)
        good = v is not None and "GATE FAIL" in v[1]
        ok &= good
        rows.append(("VERDICT", "CTRLGRADED graded only in verification/campaign",
                     "GATE FAIL found", str(v[1]) if v else "NOT FOUND",
                     "PASS" if good else "FAIL"))
        v = find_verdict("CTRLRAN", vidx)
        good = v is None
        ok &= good
        rows.append(("VERDICT", "CTRLRAN has no campaign record",
                     "None", str(v), "PASS" if good else "FAIL"))
        # Substring-collision control: plant F17's verdict, ask for F1's.  A
        # bare `k in name` match returns F17's record and marks F1 graded.
        _w(os.path.join(camp, "F17_KV40_RESULTS.md"), "F17 verdict: PASS\n")
        vidx2 = build_verdict_index([camp])
        v = find_verdict("F1", vidx2)
        good = v is None
        ok &= good
        rows.append(("VERDICT", "family F1 must NOT match F17_KV40_RESULTS.md",
                     "None", str(v[0]) if v else "None", "PASS" if good else "FAIL"))
        v = find_verdict("F17", vidx2)
        good = v is not None
        ok &= good
        rows.append(("VERDICT", "family F17 DOES match F17_KV40_RESULTS.md",
                     "found", "found" if v else "NOT FOUND",
                     "PASS" if good else "FAIL"))

        # --- orphan-run-dir control: a case that ran and was then PRUNED must
        #     be seen by the second unit, and an empty dir must not be ---
        orphans = discover_orphan_run_dirs(roots, [cr for cr, _a, _b in found])
        opaths = {o["case_root"] for o in orphans}
        pruned = os.path.join(base, "verification", "runs", "CTRLPRUNED_runs", "L1")
        good = pruned in opaths
        ok &= good
        rows.append(("ORPHAN", "pruned case (ran, system/ deleted) is seen",
                     "RAN_LOGS_ONLY", "seen" if good else "MISSED",
                     "PASS" if good else "FAIL"))
        empty = os.path.join(base, "verification", "runs", "CTRLEMPTY_runs", "L1")
        good = empty not in opaths
        ok &= good
        rows.append(("ORPHAN", "empty run dir is NOT called run",
                     "absent", "absent" if good else "WRONGLY PRESENT",
                     "PASS" if good else "FAIL"))
        # a mesh-only orphan (blockMesh log, no solver) must not count as run
        mo = os.path.join(base, "verification", "runs", "CTRLMESHORPHAN_runs", "L1")
        _w(os.path.join(mo, "log.blockMesh"), _MESH_LOG)
        _w(os.path.join(mo, "log.checkMesh"), _CHECKMESH_LOG)
        orphans2 = discover_orphan_run_dirs(roots, [cr for cr, _a, _b in found])
        good = mo not in {o["case_root"] for o in orphans2}
        ok &= good
        rows.append(("ORPHAN", "mesh-only orphan is NOT called run",
                     "absent", "absent" if good else "WRONGLY PRESENT",
                     "PASS" if good else "FAIL"))

        # --- family_key control: verification/runs/<CAMPAIGN> must NOT
        #     collapse to "runs" (it did, silently, in the first census) ---
        for probe, want in (
            ("verification/runs/F19_SOD_runs/coarse", "F19_SOD"),
            ("verification/runs/MODEL_FORM_runs/B_re1p2e7_kEpsilon", "MODEL_FORM"),
            ("cases/F19_SOD/case", "F19_SOD"),
            ("models/tmr/flatplate", "tmr"),
        ):
            got = family_key(os.path.join(REPO, probe))
            good = got == want
            ok &= good
            rows.append(("FAMILY", probe, want, got, "PASS" if good else "FAIL"))

        # --- REFUSAL control: an unknown time-looping binary must raise ---
        r = _mkcase(os.path.join(base, "refuse", "CTRLUNKNOWN_runs", "L1"))
        _w(os.path.join(r, "log.quantumFoam"), _UNKNOWN_SOLVER_LOG)
        try:
            classify_case(r, True, False)
            rows.append(("REFUSAL", "unknown binary quantumFoam", "Refusal raised",
                         "no refusal", "FAIL"))
            ok = False
        except Refusal:
            rows.append(("REFUSAL", "unknown binary quantumFoam", "Refusal raised",
                         "Refusal raised", "PASS"))

        # --- MUTATION control: break the reader, prove the control catches it ---
        # A reader that only trusts the Exec banner must FAIL the fixture.
        real = globals()["_attribute_binary"]

        def banner_only(path, text):
            for line in text.split("\n", 60)[:60]:
                if line.startswith("Exec") and ":" in line:
                    return os.path.basename(line.split(":", 1)[1].strip().split()[0]), "banner"
            return "<none>", "none"

        hid = os.path.join(base, "verification", "runs", "CTRLHIDDEN_runs",
                           "deep", "nest", "case")
        globals()["_attribute_binary"] = banner_only
        try:
            # A banner-only reader cannot attribute the stripped log.  Either
            # outcome proves the mutation was DETECTED: it refuses, or it sees
            # zero solver logs.  What must NOT happen is a silent RAN_COMPLETE
            # produced by the same code path the real reader uses.
            try:
                mutated = classify_case(hid, True, False)
                observed = f"{len(mutated['solver_logs'])} solver logs"
                good = len(mutated["solver_logs"]) == 0
            except Refusal:
                observed = "Refusal raised"
                good = True
        finally:
            globals()["_attribute_binary"] = real
        ok &= good
        rows.append(("MUTATION", "banner-only reader cannot see the stripped log",
                     "refuse or 0 logs", observed, "PASS" if good else "FAIL"))
        # and with the real reader it must see it
        det = classify_case(os.path.join(base, "verification", "runs",
                                         "CTRLHIDDEN_runs", "deep", "nest", "case"),
                            True, False)
        good = len(det["solver_logs"]) == 1
        ok &= good
        rows.append(("MUTATION", "real reader sees the stripped log",
                     "1 solver log", f"{len(det['solver_logs'])}",
                     "PASS" if good else "FAIL"))
    finally:
        shutil.rmtree(base, ignore_errors=True)

    if verbose:
        print("PLANTED CONTROL -- scripts/census_never_run.py")
        print(f"{'check':<12} {'planted':<58} {'expected':<22} {'observed':<22} verdict")
        print("-" * 128)
        for c, name, want, got, res in rows:
            print(f"{c:<12} {name[:58]:<58} {str(want)[:22]:<22} {str(got)[:22]:<22} {res}")
        print("-" * 128)
        npass = sum(1 for r in rows if r[4] == "PASS")
        print(f"{npass}/{len(rows)} control checks PASS -> "
              f"{'CONTROL PASS' if ok else 'CONTROL FAIL'}")
    return ok


# ----------------------------------------------------------------- census ----


def run_census():
    territory = []
    cdir = os.path.join(REPO, "cases")
    for d in sorted(os.listdir(cdir)):
        if d in CASES_EXCLUDE:
            continue
        p = os.path.join(cdir, d)
        if os.path.isdir(p):
            territory.append(p)
    rdir = os.path.join(REPO, "verification", "runs")
    for d in sorted(os.listdir(rdir)):
        if d in RUNS_EXCLUDE:
            continue
        p = os.path.join(rdir, d)
        if os.path.isdir(p):
            territory.append(p)
    territory.append(os.path.join(REPO, "models"))

    roots = discover_case_roots(territory)
    vidx = build_verdict_index([os.path.join(REPO, "verification", "campaign")])

    out = []
    for cr, has_cd, has_tpl in roots:
        out.append(classify_case(cr, has_cd, has_tpl))
    out.extend(discover_orphan_run_dirs(territory, [r[0] for r in roots]))

    for ev in out:
        fk = family_key(ev["case_root"])
        ev["family"] = fk
        v = find_verdict(fk, vidx)
        ev["verdict_path"] = v[0] if v else None
        ev["verdict_tokens"] = v[1] if v else []
        ev["graded"] = bool(v)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted control only")
    ap.add_argument("--census", action="store_true",
                    help="run the control, then the census (refuses if control fails)")
    ap.add_argument("--json", metavar="PATH", help="write the full census as JSON")
    ap.add_argument("--tsv", metavar="PATH",
                    help="write the census as one TSV row per case root")
    ap.add_argument("--class", dest="klass", help="print only rows of this class")
    args = ap.parse_args()

    if not (args.selftest or args.census):
        ap.error("one of --selftest or --census is required")

    ok = selftest(verbose=True)
    if not ok:
        print("\nREFUSING: the planted control did not pass. A zero from a reader "
              "not shown able to see a non-zero is not evidence (CLAUDE.md rule 3).",
              file=sys.stderr)
        return 2
    if args.selftest and not args.census:
        return 0

    print()
    try:
        rows = run_census()
    except Refusal as e:
        print(f"\nREFUSING: {e}", file=sys.stderr)
        return 2

    counts = {}
    for r in rows:
        counts[r["klass"]] = counts.get(r["klass"], 0) + 1

    print("CENSUS -- cfd territory")
    print("  unit:      a directory D with D/system/controlDict (case INSTANCE)")
    print("             or D/system/controlDict*.template (case DEFINITION)")
    print("  territory: cases/ minus {RANS_LES_closure_models, dafoam};")
    print("             verification/runs/ minus {T-family, F14-cooling-ladder,")
    print("             THERMAL_K0_runs}; models/")
    print(f"  case roots discovered: {len(rows)}")
    print()
    for k in sorted(counts):
        print(f"  {k:<16} {counts[k]:>5}")
    print()

    never = [r for r in rows if r["klass"] == "NEVER_RUN"]
    cannot = [r for r in rows if r["missing_binary"]]
    print(f"  NEVER_RUN predicate: no solver log with an 'ExecutionTime = ' line,")
    print(f"    no time directory > 0 with content (case level OR processor*/),")
    print(f"    and no mesh (constant/polyMesh/points or a mesh-utility log).")
    print(f"  NEVER_RUN case roots: {len(never)}")
    print(f"  CANNOT_RUN_WITH_OPENFOAM (controlDict application binary absent): "
          f"{len(cannot)}")
    for r in cannot:
        print(f"    {os.path.relpath(r['case_root'], REPO)}  missing: {r['missing_binary']}")
    print()

    # family rollup
    fam = {}
    for r in rows:
        f = fam.setdefault(r["family"], {"n": 0, "ran": 0, "never": 0, "mesh": 0,
                                         "init": 0, "tpl": 0, "graded": False,
                                         "verdict": None})
        f["n"] += 1
        k = r["klass"]
        if k.startswith("RAN"):
            f["ran"] += 1
        elif k == "NEVER_RUN":
            f["never"] += 1
        elif k == "MESH_ONLY":
            f["mesh"] += 1
        elif k == "INIT_ONLY":
            f["init"] += 1
        elif k == "TEMPLATE_ONLY":
            f["tpl"] += 1
        if r["graded"]:
            f["graded"] = True
            f["verdict"] = r["verdict_path"]

    print("FAMILY ROLLUP  (a family is NEVER RUN only if ran==0 and init==0)")
    print(f"{'family':<34}{'roots':>6}{'ran':>5}{'init':>5}{'mesh':>5}{'never':>6}"
          f"{'tpl':>5}  verdict artifact")
    print("-" * 128)
    for k in sorted(fam):
        f = fam[k]
        v = os.path.relpath(f["verdict"], REPO) if f["verdict"] else "-- none found --"
        print(f"{k:<34}{f['n']:>6}{f['ran']:>5}{f['init']:>5}{f['mesh']:>5}"
              f"{f['never']:>6}{f['tpl']:>5}  {v}")
    print("-" * 128)
    dead = [k for k, f in fam.items() if f["ran"] == 0 and f["init"] == 0 and f["tpl"] < f["n"]]
    print(f"families with ZERO solve evidence anywhere: {len(dead)}")
    for k in sorted(dead):
        print(f"  {k}")

    if args.klass:
        print()
        print(f"--- rows in class {args.klass} ---")
        for r in rows:
            if r["klass"] == args.klass:
                print(f"  {os.path.relpath(r['case_root'], REPO)}")
                print(f"      evidence: {os.path.relpath(r['evidence_path'], REPO)}")

    if args.tsv:
        with open(args.tsv, "w") as fh:
            fh.write("# cfd-territory never-run census -- generated by "
                     "scripts/census_never_run.py\n")
            fh.write("# unit: directory D with D/system/controlDict (INSTANCE) or "
                     "D/system/controlDict*.template (DEFINITION); plus the orphan\n"
                     "#       unit: a directory with solver logs and NO system/ "
                     "(a case run then pruned) -> RAN_LOGS_ONLY\n")
            fh.write("# NEVER_RUN predicate: no solver log with an 'ExecutionTime = ' "
                     "line, no time dir > 0 with content (case level OR processor*/),\n"
                     "#                      and no mesh (constant/polyMesh/points or "
                     "a mesh-utility log).\n")
            fh.write("# family is NAME-DERIVED and is a navigation aid only -- it "
                     "cannot reliably pair a definition under cases/ with its\n"
                     "# outputs under verification/runs/, and it collides "
                     "(cases/tmr and models/tmr share the key 'tmr').\n")
            fh.write("# verdict_artifact is NAME-LINKED and is the weakest column "
                     "here; open it before relying on it.\n")
            fh.write("class\tfamily\tcase_root\tevidence_path\tapplication\t"
                     "missing_binary\tsolver_logs\ttime_dirs\tproc_time_dirs\t"
                     "end_line\trc\tverdict_tokens\tverdict_artifact\n")
            for r in sorted(rows, key=lambda x: (x["klass"], x["case_root"])):
                fh.write("\t".join([
                    r["klass"],
                    r.get("family", ""),
                    os.path.relpath(r["case_root"], REPO),
                    os.path.relpath(r["evidence_path"], REPO),
                    str(r.get("application") or ""),
                    str(r.get("missing_binary") or ""),
                    str(len(r.get("solver_logs") or [])),
                    str(len(r.get("time_dirs") or [])),
                    str(len(r.get("processor_time_dirs") or [])),
                    "1" if r.get("end_line") else "0",
                    str(r.get("rc") or ""),
                    ",".join(r.get("verdict_tokens") or []),
                    os.path.relpath(r["verdict_path"], REPO) if r.get("verdict_path") else "",
                ]) + "\n")
        print(f"\nTSV: {args.tsv}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"unit": "case root (system/controlDict or controlDict*.template)",
                       "counts": counts, "rows": rows}, fh, indent=1)
        print(f"\nJSON: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
