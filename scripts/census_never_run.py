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

v2, 2026-09-04 -- THE OUT-OF-GIT DEFECT.  v1 never looked outside the
repository.  CLAUDE.md: "Data too large for git lives outside it --
/home/ubuntu/{closure-data, closure-challenge-benchmark, certonomous-runs}/.
Nothing is invisible merely because it is big; docs/LOCATIONS.md enumerates it."
Measured cost of the blindness: verification/runs/F5_runs/re2000/case was
classified NEVER_RUN, while /home/ubuntu/certonomous-runs/f5a-cylinder-ladder/
re2000 holds 90/{U,p,phi,uniform,yPlus} at its controlDict endTime of 90.0 and a
forceCoeffs coefficient.dat of 10,191 data rows whose last time is exactly 90.
Four defects, four repairs:

  (a) TERRITORY.  The out-of-git roots are ENUMERATED FROM docs/LOCATIONS.md
      (locations_named_dirs), never hard-coded.  Every top-level directory of
      /home/ubuntu is then WALKED and its case roots counted, so a store that
      holds cases and is NOT named in LOCATIONS.md is a REPORTED DISAGREEMENT
      (reconcile_out_of_git) rather than a silent omission -- and it is
      censused anyway, because blindness is the defect being repaired.

  (b) PHYSICS vs BOOKKEEPING.  re2000's solver log is GONE (only log.blockMesh
      and log.checkMesh survive), so CLAUDE.md rule 4 cannot be certified for
      it.  Under Sanaa's universal rule "bookkeeping never voids physics" the
      fields still stand.  Collapsing that into RAN_COMPLETE claims a
      completion nobody can check; collapsing it into NEVER_RUN throws away a
      solve.  It is its own class, RAN_PHYSICS_NO_LOG, and every row carries
      two INDEPENDENT columns -- `physics` (field data on disk: NONE /
      PROCESSOR_ONLY / PARTIAL_FIELDS / ENDTIME_FIELDS) and `bookkeeping`
      (ABSENT / INCOMPLETE / COMPLETE) -- so the two are never conflated again.

  (c) THE LINK, and why it is not a name match.  A previous lane's stem-pairing
      had false negatives and this script refused to repeat it.  It does not
      have to: verification/runs/F5_runs/<rung>/stage_params.json carries
      `"remote_dir": "/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/<rung>"`
      -- a POINTER RECORDED BY THE STAGING CODE ITSELF, at stage time.  A case
      root whose own artifacts show nothing but whose recorded remote_dir has
      solve evidence is RAN_AT_LINKED_REMOTE, with the remote artifact printed.

  (d) ATTRIBUTION AND THE REFUSAL.  Out of git, 2,659 log files carry
      ExecutionTime lines and 486 distinct filename stems are not binary names
      at all (driver wrappers: `S3_r1_20260826T033053Z_3069758.log`).  Two
      repairs: the Exec banner is now sought ANYWHERE in the log and yields a
      SET (A2-GC-wing-grid-convergence/L1_attempt3_CAPSTOP/mesh.log carries
      plot3dToFoam at line 69, autoPatch at 180 and createPatch at 225 -- all
      three past v1's 60-line window); and a log that yields NO name from
      either channel is UNATTRIBUTED.  In the repository the refusal is
      UNCHANGED -- strict=True, an unattributed time loop still exits 2.  Out
      of git it is recorded as RAN_UNATTRIBUTED_LOG: a third state that says
      "a time loop ran here and this script cannot say which binary", which is
      the truth, instead of a RAN that could hide a decomposePar or a
      NEVER_RUN that could hide a solve.

  KNOWN RESIDUAL LIMIT, stated rather than papered over: an in-repo case whose
  work happened out of git under a name this script cannot link -- no recorded
  remote_dir -- is still classified on its own artifacts alone and can still
  read NEVER_RUN.  Name-matching would close it and would reintroduce exactly
  the false-negative class the F1-vs-F17 control exists to catch.  Such rows
  are adjudicated by hand, not by this script.

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

  E_end_t    the case's controlDict endTime, and whether a time directory of
             exactly that value holds >=1 regular file.  This is the PHYSICS
             half of CLAUDE.md rule 4's completion test and it does not need
             the solver log.
  E_series   the last time in the case's postProcessing coefficient series
             (postProcessing/**/coefficient*.dat), and whether it reaches
             endTime.  Also physics; also independent of the log.
  E_remote   a POINTER, recorded by the staging code itself, from a JSON file
             at the case root or its parent carrying a top-level "remote_dir"
             key naming a directory that exists.  Not a name match.

CLASSES (mutually exclusive, evaluated in this order):
  TEMPLATE_ONLY   no system/controlDict; only a controlDict*.template.  A case
                  DEFINITION.  Not evidence of anything having run, and not
                  itself a runnable unit -- its instances are counted elsewhere.
  RAN             E_log from a SOLVER binary, OR E_time, OR E_ptime.
                  Sub-labelled COMPLETE when E_end holds and RC is absent or 0.
  RAN_PHYSICS_NO_LOG
                  E_time or E_ptime hold -- field data written by a time loop
                  -- and there is NO solver log at all.  The physics is on
                  disk; the bookkeeping rule 4 needs is gone.  Read the row's
                  `physics` and `bookkeeping` columns; do not read this class
                  as either a completion or an absence.
  RAN_UNATTRIBUTED_LOG
                  a log with ExecutionTime lines that this script cannot
                  attribute to any binary, and no other solve evidence.  A
                  time loop ran; which binary is unknown.  OUT-OF-GIT ONLY --
                  inside the repository this is still a refusal (exit 2).
  RAN_AT_LINKED_REMOTE
                  this case root shows no solve evidence of its own, but the
                  remote_dir its own staging record names does.  The remote
                  artifact is printed; the remote's class is carried in
                  `remote_klass`.
  INIT_ONLY       E_log holds but every time-looping log attributes to
                  INIT_ONLY_BINS (potentialFoam), and no E_time/E_ptime.
                  Potential-flow initialisation is not the case's solve.
  MESH_ONLY       no solve evidence, but E_mesh.
  NEVER_RUN       no solve evidence and no mesh evidence.

TWO INDEPENDENT COLUMNS, never collapsed into the class (the graders split
these and so does this):
  physics       NONE | PROCESSOR_ONLY | PARTIAL_FIELDS | ENDTIME_FIELDS
  bookkeeping   ABSENT | INCOMPLETE | COMPLETE
A row can be ENDTIME_FIELDS/ABSENT (re2000) or NONE/COMPLETE (a solver log
whose fields were deleted).  Neither is expressible as one label.

SCOPE OF `bookkeeping = ABSENT`, stated because it is easy to over-read: it
means NO SOLVER LOG AT THE CASE ROOT (or its logs/ subdirectory), which is
where _log_files looks.  It does NOT mean no log exists anywhere in the lab.
Out of git, driver harnesses commonly write one wrapper log at the STUDY root
covering many sub-cases; those sub-cases read ABSENT here and their evidence
is one level up.  Treat ABSENT as "not certifiable from this directory", not
as "the run was never recorded".

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
    # Added 2026-09-04 when the census was extended out of git, and added
    # DELIBERATELY: it is the ONLY unknown named binary in the whole extended
    # territory (29 logs, all under /home/ubuntu/closure-data/r5c/).  Verified
    # before adding, not assumed from the name: the binary exists at
    # /home/ubuntu/OpenFOAM/ubuntu-v2606/platforms/linux64GccDPInt32Opt/bin/
    # kCorrectiveFrozenFoamV2 (674,384 bytes, 2026-08-22) and is named in
    # cases/RANS_LES_closure_models/R5C_omega_repair/PREREGISTRATION.md.
    "kCorrectiveFrozenFoamV2",
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

# ------------------------------------------------------- out-of-git roots ----
# CLAUDE.md: "Data too large for git lives outside it ... Nothing is invisible
# merely because it is big; docs/LOCATIONS.md enumerates it."  The roots are
# read FROM that index, never hard-coded here -- a hard-coded list is a second
# place to forget a store, which is the defect this repairs.
HOME = os.path.expanduser("~")
LOCATIONS_INDEX = os.path.join(REPO, "docs", "LOCATIONS.md")
_HOME_PATH_RE = re.compile(r"/home/ubuntu/([A-Za-z0-9][A-Za-z0-9._+-]*)")
# A python venv or a node tree can hold thousands of directories and no case.
OUT_OF_GIT_PRUNE = PRUNE_DIRS | {
    "node_modules", "site-packages", ".venv", "venv", ".tox", ".mypy_cache",
}
# JSON keys under which the staging code records where it copied the case to.
REMOTE_DIR_KEYS = ("remote_dir", "remote_case", "run_dir")

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


def _known_binary(name):
    return name in SOLVERS or name in INIT_ONLY_BINS or name in UTILITIES


def _log_stem(path):
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
    return stem.split(".")[0]


def _attribute_binaries(path, text):
    """The SET of binaries that produced this log, and how it was attributed.

    Two changes from v1, both paid for by measurement on this corpus:

    1. The Exec banner is sought ANYWHERE in the log, not in the first 60
       lines.  A wrapper log holds several: /home/ubuntu/certonomous-runs/
       A2-GC-wing-grid-convergence/L1_attempt3_CAPSTOP/mesh.log carries
       plot3dToFoam at line 69, autoPatch at 180 and createPatch at 225.  A
       60-line, single-valued reader saw none of them and fell through to the
       filename stem "mesh", which is not a binary.

    2. The filename fallback is accepted ONLY when the stem IS a known binary
       name.  Out of git, 486 distinct stems are run names, not binaries
       (`S3_r1_20260826T033053Z_3069758.log`).  Returning those as binaries
       turned every one of them into a refusal.

    Returns (set_of_binaries, how) where how is "banner", "filename" or
    "unattributed".  An empty set means: a time loop may well have run here
    and this script cannot say what produced it.  That is a THIRD state, and
    the caller decides -- refuse in the repository, record outside it.
    """
    bins = set()
    for line in text.split("\n"):
        if line.startswith("Exec") and ":" in line:
            tail = line.split(":", 1)[1].strip()
            if tail:
                bins.add(os.path.basename(tail.split()[0]))
    if bins:
        return bins, "banner"
    stem = _log_stem(path)
    if _known_binary(stem):
        return {stem}, "filename"
    return set(), "unattributed"


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


def _controldict_end_time(case_root):
    """The case's own endTime, as a float.  The PHYSICS half of rule 4's
    completion test: it lets `did the run reach the time it was told to reach`
    be answered from the fields alone, with no solver log."""
    p = os.path.join(case_root, "system", "controlDict")
    if not os.path.isfile(p):
        return None
    try:
        txt = open(p, errors="replace").read(200000)
    except OSError:
        return None
    m = re.search(r"^\s*endTime\s+([0-9eE.+-]+)\s*;", txt, re.M)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _series_last_time(case_root, cap=200):
    """(path, last time) of the case's postProcessing coefficient series.

    Independent of the solver log and of the time directories: a forceCoeffs
    series that reaches endTime is a time loop that reached endTime.  Measured
    on the worked example: .../f5a-cylinder-ladder/re2000/postProcessing/
    forceCoeffs1/0/coefficient.dat, 10,191 data rows, last time 90, against a
    controlDict endTime of 90.0.
    """
    ppd = os.path.join(case_root, "postProcessing")
    if not os.path.isdir(ppd):
        return None, None
    best = (None, None)
    seen = 0
    for dp, _dn, fn in os.walk(ppd):
        for f in sorted(fn):
            if not (f.startswith("coefficient") and f.endswith(".dat")):
                continue
            seen += 1
            if seen > cap:
                return best
            p = os.path.join(dp, f)
            last = None
            try:
                with open(p, errors="replace") as fh:
                    for line in fh:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        tok = line.split()[0]
                        try:
                            last = float(tok)
                        except ValueError:
                            pass
            except OSError:
                continue
            if last is not None and (best[1] is None or last > best[1]):
                best = (p, last)
    return best


def _linked_remote_dirs(case_root):
    """Directories this case's OWN staging record points at.

    NOT a name match.  verification/runs/F5_runs/re2000/stage_params.json is
    written by verification/runs/F5_runs/run_rung.py:77 and carries
    "remote_dir": "/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re2000".
    The pointer was recorded by the code that did the staging, at the time it
    staged; it cannot collide the way F1 collides with F17_KV40.

    Looked for at the case root AND at its parent, because run_rung.py stages
    <rung>/case and writes the record one level up at <rung>/.
    """
    out = []
    for d in (case_root, os.path.dirname(case_root)):
        if not os.path.isdir(d):
            continue
        try:
            entries = sorted(os.listdir(d))
        except OSError:
            continue
        for f in entries:
            if not f.endswith(".json"):
                continue
            p = os.path.join(d, f)
            if not os.path.isfile(p):
                continue
            try:
                obj = json.loads(_read_text(p, 4 * 1024 * 1024))
            except Exception:
                continue
            if not isinstance(obj, dict):
                continue
            for key in REMOTE_DIR_KEYS:
                v = obj.get(key)
                if not isinstance(v, str) or not v:
                    continue
                v = os.path.abspath(os.path.expanduser(v))
                if v == os.path.abspath(case_root):
                    continue
                if os.path.isdir(v) and v not in [r[1] for r in out]:
                    out.append((p, v))
    return out


# ------------------------------------------------------------- discovery -----


def discover_case_roots(territory_roots, prune=None):
    """Every case root under the given roots.  See PREDICATES: CENSUS UNIT."""
    prune = PRUNE_DIRS if prune is None else prune
    found = []
    for root in territory_roots:
        if not os.path.isdir(root):
            continue
        for dp, dn, _fn in os.walk(root):
            dn[:] = [
                d for d in dn
                if d not in prune
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


def classify_case(case_root, has_cd, has_tpl, strict=True, follow_remote=True):
    """Classify one case root.

    strict=True  -- the repository.  An unattributed time-looping log RAISES,
                    exactly as v1 did.  The calibration behind that refusal was
                    taken on this tree and still holds here.
    strict=False -- an out-of-git store.  That refusal was NOT calibrated
                    there: 486 distinct log stems out of git are run names, not
                    binaries.  An unattributed time loop is RECORDED as its own
                    state rather than guessed in either direction.
    """
    ev = {
        "case_root": case_root,
        "has_controlDict": has_cd,
        "has_template": has_tpl,
        "time_dirs": [],
        "processor_time_dirs": [],
        "solver_logs": [],
        "init_logs": [],
        "mesh_logs": [],
        "unattributed_logs": [],
        "end_line": False,
        "rc": None,
        "mesh_points": False,
        "application": None,
        "missing_binary": None,
        "end_time": None,
        "endtime_fields": False,
        "series_path": None,
        "series_last_time": None,
        "series_reaches_end_time": None,
        "remote_dirs": [],
        "remote_klass": None,
        "strict": strict,
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
        bins, how = _attribute_binaries(lp, text)
        if bins & MESH_BINS:
            ev["mesh_logs"].append({"path": lp,
                                    "binary": sorted(bins & MESH_BINS)[0]})
        if nexec == 0:
            continue
        rec = {"path": lp, "binary": ",".join(sorted(bins)) or "<unattributed>",
               "attribution": how,
               "execution_time_lines": nexec, "end_line": has_end}
        if bins & SOLVERS:
            ev["solver_logs"].append(rec)
            if has_end:
                ev["end_line"] = True
        elif bins & INIT_ONLY_BINS:
            ev["init_logs"].append(rec)
        elif bins & UTILITIES:
            pass
        elif not bins:
            # No Exec banner anywhere and a filename stem that is not a binary
            # name.  This is NOT the same finding as an unknown binary, and
            # collapsing the two is what made 486 driver-wrapper logs look like
            # 486 unknown solvers.
            if strict:
                raise Refusal(
                    f"unattributed time-looping log ({nexec} ExecutionTime "
                    f"lines, no Exec banner, stem {_log_stem(lp)!r} is not a "
                    f"known binary) in {lp}. Inside the repository this is a "
                    "refusal, not a guess."
                )
            ev["unattributed_logs"].append(rec)
        else:
            raise Refusal(
                f"unknown time-looping binary {sorted(bins)!r} "
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

    # ---- PHYSICS half of rule 4, measured without the solver log ----
    et = _controldict_end_time(case_root)
    ev["end_time"] = et
    if et is not None:
        for t in ev["time_dirs"]:
            try:
                if abs(float(t) - et) <= 1e-9 * max(1.0, abs(et)):
                    ev["endtime_fields"] = True
                    break
            except ValueError:
                pass
    sp, sl = _series_last_time(case_root)
    ev["series_path"], ev["series_last_time"] = sp, sl
    if sl is not None and et is not None:
        ev["series_reaches_end_time"] = sl >= et - 1e-9 * max(1.0, abs(et))

    # ---- class assignment, in order ----
    solve_evidence = bool(ev["solver_logs"] or ev["time_dirs"] or ev["processor_time_dirs"])
    mesh_evidence = bool(ev["mesh_points"] or ev["mesh_logs"])
    rc_ok = ev["rc"] in (None, "", "0")

    # Two INDEPENDENT axes.  Never fold one into the other.
    if ev["endtime_fields"]:
        ev["physics"] = "ENDTIME_FIELDS"
    elif ev["time_dirs"]:
        ev["physics"] = "PARTIAL_FIELDS"
    elif ev["processor_time_dirs"]:
        ev["physics"] = "PROCESSOR_ONLY"
    else:
        ev["physics"] = "NONE"
    if not ev["solver_logs"]:
        ev["bookkeeping"] = "ABSENT"
    elif ev["end_line"] and rc_ok:
        ev["bookkeeping"] = "COMPLETE"
    else:
        ev["bookkeeping"] = "INCOMPLETE"

    if not has_cd and has_tpl:
        cls = "TEMPLATE_ONLY"
    elif solve_evidence:
        if ev["solver_logs"]:
            cls = "RAN_COMPLETE" if (ev["end_line"] and rc_ok) else "RAN_INCOMPLETE"
        else:
            # Field data written by a time loop, and no solver log at all.
            # rule 4 cannot be certified; "bookkeeping never voids physics"
            # says the fields still stand.  Its own class, so neither claim is
            # made on the reader's behalf.
            cls = "RAN_PHYSICS_NO_LOG"
    elif ev["unattributed_logs"]:
        cls = "RAN_UNATTRIBUTED_LOG"
    elif ev["init_logs"]:
        cls = "INIT_ONLY"
    elif mesh_evidence:
        cls = "MESH_ONLY"
    else:
        cls = "NEVER_RUN"

    # ---- the recorded pointer, consulted only when this root shows nothing --
    if follow_remote and cls in ("NEVER_RUN", "MESH_ONLY", "TEMPLATE_ONLY"):
        for rec_path, rdir in _linked_remote_dirs(case_root):
            r_has_cd = os.path.isfile(os.path.join(rdir, "system", "controlDict"))
            try:
                rev = classify_case(rdir, r_has_cd, False, strict=False,
                                    follow_remote=False)
            except Refusal:
                continue
            if rev["klass"] in ("RAN_COMPLETE", "RAN_INCOMPLETE",
                                "RAN_PHYSICS_NO_LOG", "RAN_UNATTRIBUTED_LOG"):
                ev["remote_dirs"].append({"record": rec_path, "dir": rdir,
                                          "klass": rev["klass"],
                                          "physics": rev["physics"],
                                          "bookkeeping": rev["bookkeeping"],
                                          "evidence_path": rev["evidence_path"]})
                ev["remote_klass"] = rev["klass"]
                ev["physics"] = rev["physics"]
                ev["bookkeeping"] = rev["bookkeeping"]
                cls = "RAN_AT_LINKED_REMOTE"
                break

    ev["klass"] = cls
    ev["evidence_path"] = _pick_evidence_path(ev, cls)
    return ev


def _pick_evidence_path(ev, cls):
    """The single artifact a reader should open to check this classification."""
    if cls == "RAN_AT_LINKED_REMOTE" and ev.get("remote_dirs"):
        return ev["remote_dirs"][0]["evidence_path"]
    if cls == "RAN_UNATTRIBUTED_LOG" and ev.get("unattributed_logs"):
        return ev["unattributed_logs"][0]["path"]
    if cls == "RAN_PHYSICS_NO_LOG":
        if ev.get("series_path"):
            return ev["series_path"]
        if ev["time_dirs"]:
            return os.path.join(ev["case_root"], sorted(ev["time_dirs"])[0])
        if ev["processor_time_dirs"]:
            return os.path.join(ev["case_root"], sorted(ev["processor_time_dirs"])[0])
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
    ap = os.path.abspath(case_root)
    if not (ap == repo or ap.startswith(repo + os.sep)):
        # OUT OF GIT.  /home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re2000
        # -> "f5a-cylinder-ladder", prefixed with the store so a family key can
        # never silently merge an out-of-git study with a repository campaign.
        parts = [p for p in ap.split(os.sep) if p]
        try:
            i = parts.index(os.path.basename(HOME))
            store = parts[i + 1]
            study = parts[i + 2] if len(parts) > i + 2 else store
        except (ValueError, IndexError):
            return "oog:" + parts[-1]
        return f"oog:{store}/{study}"
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


def discover_orphan_run_dirs(territory_roots, case_roots, strict=True, prune=None):
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
    prune = PRUNE_DIRS if prune is None else prune
    orphans = []
    for root in territory_roots:
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in prune and not _is_time_name(d)
                     and not d.startswith("processor")]
            if dp in known or os.path.isdir(os.path.join(dp, "system")):
                continue
            if any(os.path.dirname(dp) == k or dp.startswith(k + os.sep) for k in known):
                continue
            logs = []
            unattr = []
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
                bins, how = _attribute_binaries(p, text)
                if bins & SOLVERS:
                    logs.append({"path": p, "binary": ",".join(sorted(bins & SOLVERS)),
                                 "execution_time_lines": nexec})
                elif bins & (INIT_ONLY_BINS | UTILITIES):
                    continue
                elif not bins:
                    if strict:
                        raise Refusal(
                            f"unattributed time-looping log in orphan dir {p} "
                            f"({nexec} ExecutionTime lines, stem "
                            f"{_log_stem(p)!r} is not a known binary)"
                        )
                    unattr.append({"path": p, "binary": "<unattributed>",
                                   "execution_time_lines": nexec})
                else:
                    raise Refusal(
                        f"unknown time-looping binary {sorted(bins)!r} in orphan dir {p}"
                    )
            if logs or unattr:
                orphans.append({"case_root": dp,
                                "klass": "RAN_LOGS_ONLY" if logs
                                else "RAN_UNATTRIBUTED_LOG",
                                "solver_logs": logs,
                                "unattributed_logs": unattr,
                                "has_controlDict": False,
                                "has_template": False, "missing_binary": None,
                                "application": None,
                                "physics": "NONE",
                                "bookkeeping": "INCOMPLETE" if logs else "ABSENT",
                                "evidence_path": (logs or unattr)[0]["path"]})
    return orphans


# ------------------------------------------------------- out-of-git roots ----


def locations_named_dirs(index_path=LOCATIONS_INDEX, home=HOME, repo=REPO):
    """The set of top-level directories under /home/ubuntu that
    docs/LOCATIONS.md NAMES anywhere in its text.

    Read from the index, never hard-coded: CLAUDE.md points at LOCATIONS.md as
    the enumeration, so a store added there must reach this census without a
    code change, and a store missing from there must show up as a
    DISAGREEMENT (see reconcile_out_of_git) rather than as a silent zero.
    """
    try:
        txt = open(index_path, errors="replace").read()
    except OSError:
        return set()
    named = set()
    pat = (_HOME_PATH_RE if os.path.abspath(home) == os.path.abspath(HOME)
           else re.compile(re.escape(os.path.abspath(home).rstrip("/"))
                           + r"/([A-Za-z0-9][A-Za-z0-9._+-]*)"))
    for seg in pat.findall(txt):
        p = os.path.join(home, seg)
        if os.path.isdir(p) and not os.path.islink(p):
            named.add(os.path.abspath(p))
    named.discard(os.path.abspath(repo))
    return named


def reconcile_out_of_git(home=HOME, index_path=LOCATIONS_INDEX, prune=None,
                         repo=REPO):
    """Walk EVERY top-level directory of /home/ubuntu, count the OpenFOAM case
    roots in each, and reconcile that against what LOCATIONS.md names.

    Returns a list of {root, named_in_locations, case_roots}.  Three outcomes
    matter and all three are reported:
      named + cases      -> out-of-git census territory
      named + no cases   -> nothing to census; recorded so the reader can see
                            the index was read and the store was looked at
      NOT named + cases  -> a DISAGREEMENT between the index and the disk.  It
                            is a finding in its own right, and the store is
                            censused anyway: being unlisted is not evidence of
                            being empty, and blindness is the defect here.
    Symlinks are not followed (/home/ubuntu/evidence/runs -> ../certonomous-runs
    would otherwise double-count the whole run tree).
    """
    prune = OUT_OF_GIT_PRUNE if prune is None else prune
    named = locations_named_dirs(index_path, home, repo)
    rows = []
    try:
        entries = sorted(os.listdir(home))
    except OSError:
        return rows
    for e in entries:
        if e.startswith("."):
            continue
        p = os.path.abspath(os.path.join(home, e))
        if not os.path.isdir(p) or os.path.islink(p) or p == os.path.abspath(repo):
            continue
        found = discover_case_roots([p], prune=prune)
        rows.append({"root": p, "named_in_locations": p in named,
                     "case_roots": len(found), "roots": found})
    return rows


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


# ------------------------------------------------------------------- TSV -----

TSV_COLUMNS = ("class", "tree", "physics", "bookkeeping", "family", "case_root",
               "evidence_path", "application", "missing_binary", "solver_logs",
               "unattributed_logs", "time_dirs", "proc_time_dirs", "end_time",
               "endtime_fields", "series_last_time", "end_line", "rc",
               "remote_dir", "verdict_tokens", "verdict_artifact")


def _tsv(value):
    """A TAB or a NEWLINE inside a field silently splits or shifts a row.
    Measured: verification/campaign/CFD_NEVER_RUN_CENSUS_2026-09-04.tsv holds
    two rows whose CLASS column reads `Mon Aug 24 16:38:50 UTC 2026` -- an
    RC.txt whose second line rode straight into the file."""
    s = "" if value is None else str(value)
    return s.replace("\t", " ").replace("\r", " ").replace("\n", "\\n")


def _disp(path, repo=REPO):
    """Repository paths relative, out-of-git paths absolute.  A relative path
    beginning `../..` is a path a reader cannot open."""
    ap = os.path.abspath(path)
    if ap == repo or ap.startswith(repo + os.sep):
        return os.path.relpath(ap, repo)
    return ap


def _tsv_row(r, repo=REPO):
    rd = (r.get("remote_dirs") or [{}])[0].get("dir", "")
    return "\t".join(_tsv(v) for v in (
        r["klass"],
        r.get("tree", "repo"),
        r.get("physics", ""),
        r.get("bookkeeping", ""),
        r.get("family", ""),
        _disp(r["case_root"], repo),
        _disp(r["evidence_path"], repo),
        r.get("application") or "",
        r.get("missing_binary") or "",
        len(r.get("solver_logs") or []),
        len(r.get("unattributed_logs") or []),
        len(r.get("time_dirs") or []),
        len(r.get("processor_time_dirs") or []),
        r.get("end_time") if r.get("end_time") is not None else "",
        "1" if r.get("endtime_fields") else "0",
        r.get("series_last_time") if r.get("series_last_time") is not None else "",
        "1" if r.get("end_line") else "0",
        r.get("rc") or "",
        rd,
        ",".join(r.get("verdict_tokens") or []),
        _disp(r["verdict_path"], repo) if r.get("verdict_path") else "",
    )) + "\n"


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

    # 13. THE re2000 SHAPE -- physics complete, bookkeeping gone.  Fields at
    #     the controlDict endTime, a coefficient series that reaches endTime,
    #     mesh logs, and NO solver log at all.  Planted IN the fixture repo so
    #     the class is proved independently of the out-of-git machinery.
    r = _mkcase(os.path.join(runs, "CTRLNOLOG_runs", "L1"))
    _w(os.path.join(r, "system", "controlDict"),
       "application     pimpleFoam;\nstartTime 0;\nendTime         90.0;\n")
    _w(os.path.join(r, "constant", "polyMesh", "points"), "8\n(\n)\n")
    _w(os.path.join(r, "log.blockMesh"), _MESH_LOG)
    _w(os.path.join(r, "log.checkMesh"), _CHECKMESH_LOG)
    _w(os.path.join(r, "90", "U"), "internalField uniform (1 0 0);\n")
    _w(os.path.join(r, "90", "p"), "internalField uniform 0;\n")
    _w(os.path.join(r, "postProcessing", "forceCoeffs1", "0", "coefficient.dat"),
       "# Force coefficients\n# Time\tCd\tCl\n"
       "0.0044802867\t3.55e+02\t1.76e+02\n45\t2.0\t1.0\n90\t1.8428\t1.0073\n")
    expect[r] = "RAN_PHYSICS_NO_LOG"

    # 14. A TSV-HOSTILE field.  RC.txt with an embedded newline split a real
    #     census row in two: CFD_NEVER_RUN_CENSUS_2026-09-04.tsv carries two
    #     rows whose CLASS column reads "Mon Aug 24 16:38:50 UTC 2026".
    r = _mkcase(os.path.join(runs, "CTRLTSVBREAK_runs", "L1"))
    _w(os.path.join(r, "log.simpleFoam"), _SOLVER_LOG)
    _w(os.path.join(r, "100", "U"), "internalField uniform (1 0 0);\n")
    _w(os.path.join(r, "RC.txt"), "0\nMon Aug 24 16:38:50 UTC 2026\n")
    expect[r] = "RAN_INCOMPLETE"   # rc is not "0", so not COMPLETE

    return expect, camp


def build_out_of_git_fixture(base):
    """A SECOND tree, OUTSIDE the fixture repository, standing in for
    /home/ubuntu/certonomous-runs -- and a LOCATIONS.md that names it.

    This is the planted non-zero for the defect being repaired.  "No out-of-git
    runs" is a ZERO, and a zero from a reader not shown able to see a non-zero
    is not evidence (CLAUDE.md rule 3).  The mutation half is the v1 reader:
    roots restricted to the repository, which MUST fail to see any of this.

    Returns (home, expect, index_path).
    """
    home = os.path.join(base, "home")
    repo = os.path.join(home, "FixtureRepo")
    store = os.path.join(home, "fixture-runs")        # named in the index
    unlisted = os.path.join(home, "fixture-unlisted") # NOT named: a finding
    empty = os.path.join(home, "fixture-empty")       # named, holds no case
    os.makedirs(empty, exist_ok=True)
    expect = {}

    # (a) A completed out-of-git run.  A repo-only reader sees nothing here.
    r = _mkcase(os.path.join(store, "study-A", "rungA"))
    _w(os.path.join(r, "log.simpleFoam"), _SOLVER_LOG)
    _w(os.path.join(r, "100", "U"), "internalField uniform (1 0 0);\n")
    expect[r] = "RAN_COMPLETE"

    # (b) The re2000 shape, out of git: physics to endTime, no solver log.
    r = os.path.join(store, "study-A", "rungB")
    _w(os.path.join(r, "system", "controlDict"),
       "application     pimpleFoam;\nstartTime 0;\nendTime         90.0;\n")
    _w(os.path.join(r, "system", "fvSchemes"), "")
    _w(os.path.join(r, "0", "U"), "internalField uniform (0 0 0);\n")
    _w(os.path.join(r, "log.blockMesh"), _MESH_LOG)
    _w(os.path.join(r, "log.checkMesh"), _CHECKMESH_LOG)
    _w(os.path.join(r, "90", "U"), "internalField uniform (1 0 0);\n")
    _w(os.path.join(r, "postProcessing", "forceCoeffs1", "0", "coefficient.dat"),
       "# Time\tCd\n0.004\t3.5\n90\t1.84\n")
    expect[r] = "RAN_PHYSICS_NO_LOG"

    # (c) An UNATTRIBUTED time loop -- a driver wrapper log, no Exec banner,
    #     stem is a run name.  Refused inside the repo, recorded outside it.
    r = _mkcase(os.path.join(store, "study-B", "rungC"))
    _w(os.path.join(r, "S3_r1_20260826T033053Z_3069758.log"),
       _SOLVER_LOG_NO_BANNER)
    expect[r] = "RAN_UNATTRIBUTED_LOG"

    # (d) A DEEP Exec banner -- past v1's 60-line window, and three of them.
    r = _mkcase(os.path.join(store, "study-B", "rungD"))
    _w(os.path.join(r, "mesh.log"),
       "\n".join(["preamble line %d" % i for i in range(120)]) + "\n"
       + _MESH_LOG + _SOLVER_LOG)
    expect[r] = "RAN_COMPLETE"

    # (e) A store the index does NOT name, holding a real case.
    r = _mkcase(os.path.join(unlisted, "study-Z", "rungZ"))
    _w(os.path.join(r, "log.simpleFoam"), _SOLVER_LOG)
    _w(os.path.join(r, "100", "U"), "internalField uniform (1 0 0);\n")
    expect[r] = "RAN_COMPLETE"

    # (f) The RECORDED POINTER.  A repo case root with nothing of its own and
    #     a staging record naming (a).  Not a name match: rungA and this case
    #     root share no name component at all.
    link = _mkcase(os.path.join(repo, "verification", "runs",
                                "CTRLLINK_runs", "L1", "case"))
    _w(os.path.join(repo, "verification", "runs", "CTRLLINK_runs", "L1",
                    "stage_params.json"),
       json.dumps({"remote_dir": os.path.join(store, "study-A", "rungA")}))
    expect[link] = "RAN_AT_LINKED_REMOTE"

    # (g) NEGATIVE half of (f): a record pointing at a path that does not
    #     exist must NOT move the class.
    nolink = _mkcase(os.path.join(repo, "verification", "runs",
                                  "CTRLNOLINK_runs", "L1", "case"))
    _w(os.path.join(repo, "verification", "runs", "CTRLNOLINK_runs", "L1",
                    "stage_params.json"),
       json.dumps({"remote_dir": os.path.join(store, "study-A", "does-not-exist")}))
    expect[nolink] = "NEVER_RUN"

    index = os.path.join(base, "FIXTURE_LOCATIONS.md")
    _w(index,
       "# fixture index\n\n"
       "```\n%s/\n```\n\n"
       "The empty store `%s/` is also enumerated here.\n"
       "The repository itself lives at `%s/`.\n"
       % (store, empty, repo))
    return home, repo, store, unlisted, empty, expect, index


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
        real = globals()["_attribute_binaries"]

        def banner_only(path, text):
            for line in text.split("\n", 60)[:60]:
                if line.startswith("Exec") and ":" in line:
                    return {os.path.basename(
                        line.split(":", 1)[1].strip().split()[0])}, "banner"
            return set(), "unattributed"

        hid = os.path.join(base, "verification", "runs", "CTRLHIDDEN_runs",
                           "deep", "nest", "case")
        globals()["_attribute_binaries"] = banner_only
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
            globals()["_attribute_binaries"] = real
        ok &= good
        rows.append(("MUTATION", "banner-only reader cannot see the stripped log",
                     "refuse or 0 logs", observed, "PASS" if good else "FAIL"))
        # and with the real reader it must see it
        det = classify_case(os.path.join(base, "verification", "runs",
                                         "CTRLHIDDEN_runs", "deep", "nest", "case"),
                            True, False)
        # --- PHYSICS/BOOKKEEPING SPLIT: the re2000 shape -------------------
        nolog = os.path.join(base, "verification", "runs", "CTRLNOLOG_runs", "L1")
        nl = classify_case(nolog, True, False)
        for label, want, got in (
            ("physics reaches endTime with NO solver log", "ENDTIME_FIELDS",
             nl["physics"]),
            ("bookkeeping recorded as absent, not incomplete", "ABSENT",
             nl["bookkeeping"]),
            ("coefficient series reaches endTime", "True",
             str(nl["series_reaches_end_time"])),
            ("class is neither RAN_COMPLETE nor NEVER_RUN",
             "RAN_PHYSICS_NO_LOG", nl["klass"]),
        ):
            good = str(want) == str(got)
            ok &= good
            rows.append(("PHYSICS", label, want, got, "PASS" if good else "FAIL"))
        # MUTATION half: a reader that takes its physics from the LOG must
        # lose this case entirely.  This is the exact v1 failure.
        real_dh = globals()["_dir_has_regular_file"]
        globals()["_dir_has_regular_file"] = lambda p, cap=4000: False
        try:
            mut = classify_case(nolog, True, False)
            observed = mut["klass"]
            good = observed != "RAN_PHYSICS_NO_LOG"
        finally:
            globals()["_dir_has_regular_file"] = real_dh
        ok &= good
        rows.append(("PHYSICS", "log-blind reader LOSES the no-log run",
                     "not RAN_PHYSICS_NO_LOG", observed,
                     "PASS" if good else "FAIL"))
        # and the negative half: a run WITH a log must not be relabelled
        withlog = classify_case(os.path.join(base, "verification", "runs",
                                             "CTRLRAN_runs", "L1"), True, False)
        good = (withlog["klass"] == "RAN_COMPLETE"
                and withlog["bookkeeping"] == "COMPLETE")
        ok &= good
        rows.append(("PHYSICS", "a run WITH a log stays RAN_COMPLETE/COMPLETE",
                     "RAN_COMPLETE/COMPLETE",
                     f"{withlog['klass']}/{withlog['bookkeeping']}",
                     "PASS" if good else "FAIL"))

        # --- TSV control: an embedded newline must not split a row ---------
        brk = classify_case(os.path.join(base, "verification", "runs",
                                         "CTRLTSVBREAK_runs", "L1"), True, False)
        line = _tsv_row(brk, base)
        good = line.count("\n") == 1 and line.endswith("\n")
        ok &= good
        rows.append(("TSV", "RC.txt with an embedded newline stays ONE row",
                     "1 newline", str(line.count("\n")),
                     "PASS" if good else "FAIL"))

        good = len(det["solver_logs"]) == 1
        ok &= good
        rows.append(("MUTATION", "real reader sees the stripped log",
                     "1 solver log", f"{len(det['solver_logs'])}",
                     "PASS" if good else "FAIL"))

        # ==== OUT-OF-GIT CONTROLS =========================================
        # The planted non-zero for the defect this version repairs.  "No
        # out-of-git runs" is a zero, and a reader not shown able to see a
        # non-zero out of git cannot be trusted to report one.
        oog = tempfile.mkdtemp(prefix="census_oog_")
        try:
            (fhome, frepo, fstore, funlisted, fempty,
             oexp, findex) = build_out_of_git_fixture(oog)

            # 1. The index is READ, not hard-coded: the named store comes back,
            #    the unlisted one does not.
            named = locations_named_dirs(findex, fhome, frepo)
            good = fstore in named and fempty in named and funlisted not in named
            ok &= good
            rows.append(("LOCATIONS", "roots enumerated FROM the index file",
                         "named store yes / unlisted no",
                         f"{fstore in named}/{funlisted in named}",
                         "PASS" if good else "FAIL"))
            # negative half: an index naming nothing yields nothing.
            _w(os.path.join(oog, "EMPTY_INDEX.md"), "# names no path\n")
            good = locations_named_dirs(os.path.join(oog, "EMPTY_INDEX.md"),
                                        fhome, frepo) == set()
            ok &= good
            rows.append(("LOCATIONS", "an index naming no path yields no root",
                         "empty set", "empty" if good else "NON-EMPTY",
                         "PASS" if good else "FAIL"))

            # 2. Reconciliation: the unlisted store that HOLDS cases must be
            #    reported as a disagreement, and the named-but-empty one must
            #    be reported as empty rather than omitted.
            recon = reconcile_out_of_git(fhome, findex, OUT_OF_GIT_PRUNE, frepo)
            rmap = {r["root"]: r for r in recon}
            good = (rmap.get(funlisted, {}).get("case_roots", 0) >= 1
                    and rmap.get(funlisted, {}).get("named_in_locations") is False)
            ok &= good
            rows.append(("LOCATIONS", "unlisted store WITH cases is a disagreement",
                         "cases>=1, named=False",
                         f"{rmap.get(funlisted, {}).get('case_roots')},"
                         f"{rmap.get(funlisted, {}).get('named_in_locations')}",
                         "PASS" if good else "FAIL"))
            good = (fempty in rmap and rmap[fempty]["case_roots"] == 0
                    and rmap[fempty]["named_in_locations"] is True)
            ok &= good
            rows.append(("LOCATIONS", "named store with NO case is reported empty",
                         "cases=0, named=True",
                         f"{rmap.get(fempty, {}).get('case_roots')},"
                         f"{rmap.get(fempty, {}).get('named_in_locations')}",
                         "PASS" if good else "FAIL"))

            # 3. THE PLANT ITSELF: classify every out-of-git fixture case.
            oog_found = {}
            for store_row in recon:
                for cr, hc, ht in store_row["roots"]:
                    oog_found[cr] = classify_case(cr, hc, ht, strict=False)
            for cr, hc, ht in discover_case_roots(
                    [os.path.join(frepo, "verification", "runs")]):
                oog_found[cr] = classify_case(cr, hc, ht, strict=True)
            for cr, want in sorted(oexp.items()):
                got = oog_found.get(cr, {}).get("klass", "NOT DISCOVERED")
                good = got == want
                ok &= good
                rows.append(("OUT_OF_GIT", os.path.relpath(cr, oog), want, got,
                             "PASS" if good else "FAIL"))

            # 4. MUTATION: the v1 reader -- repository roots only.  It MUST
            #    fail to see every out-of-git plant.  Without this the pass
            #    above proves nothing about the defect.
            repo_only = dict(
                (cr, True) for cr, _a, _b in discover_case_roots([frepo]))
            missed = [cr for cr in oexp
                      if cr.startswith(fstore + os.sep)
                      or cr.startswith(funlisted + os.sep)]
            good = bool(missed) and not any(cr in repo_only for cr in missed)
            ok &= good
            rows.append(("OUT_OF_GIT",
                         "MUTATION: repo-only reader sees NONE of the plants",
                         f"0 of {len(missed)}",
                         f"{sum(1 for cr in missed if cr in repo_only)} of {len(missed)}",
                         "PASS" if good else "FAIL"))
            # and the real reader sees all of them
            good = all(cr in oog_found for cr in missed)
            ok &= good
            rows.append(("OUT_OF_GIT", "the extended reader SEES all the plants",
                         f"{len(missed)} of {len(missed)}",
                         f"{sum(1 for cr in missed if cr in oog_found)} of {len(missed)}",
                         "PASS" if good else "FAIL"))

            # 5. The unattributed log: RECORDED out of git, REFUSED in the repo.
            rc = os.path.join(fstore, "study-B", "rungC")
            try:
                classify_case(rc, True, False, strict=True)
                observed, good = "no refusal", False
            except Refusal:
                observed, good = "Refusal raised", True
            ok &= good
            rows.append(("UNATTRIBUTED",
                         "same log REFUSES under repository strictness",
                         "Refusal raised", observed, "PASS" if good else "FAIL"))

            # 6. The deep Exec banner, past v1's 60-line window.
            rd = os.path.join(fstore, "study-B", "rungD")
            txt = _read_text(os.path.join(rd, "mesh.log"))
            bins, how = _attribute_binaries(os.path.join(rd, "mesh.log"), txt)
            good = "simpleFoam" in bins and "blockMesh" in bins and how == "banner"
            ok &= good
            rows.append(("ATTRIBUTION", "banner past line 60, SET-valued",
                         "{blockMesh,simpleFoam}", ",".join(sorted(bins)),
                         "PASS" if good else "FAIL"))
            # MUTATION half: v1's 60-line single-valued reader sees neither.
            first60 = txt.split("\n", 60)[:60]
            good = not any(l.startswith("Exec") for l in first60)
            ok &= good
            rows.append(("ATTRIBUTION",
                         "MUTATION: 60-line reader finds no banner at all",
                         "no banner", "none" if good else "found",
                         "PASS" if good else "FAIL"))

            # 7. The RECORDED POINTER, and its negative half.
            link = os.path.join(frepo, "verification", "runs", "CTRLLINK_runs",
                                "L1", "case")
            lv = classify_case(link, True, False, strict=True)
            good = (lv["klass"] == "RAN_AT_LINKED_REMOTE"
                    and lv["remote_klass"] == "RAN_COMPLETE"
                    and lv["evidence_path"].startswith(fstore))
            ok &= good
            rows.append(("REMOTE_LINK", "recorded remote_dir moves the class",
                         "RAN_AT_LINKED_REMOTE", lv["klass"],
                         "PASS" if good else "FAIL"))
            nolink = os.path.join(frepo, "verification", "runs",
                                  "CTRLNOLINK_runs", "L1", "case")
            nv = classify_case(nolink, True, False, strict=True)
            good = nv["klass"] == "NEVER_RUN"
            ok &= good
            rows.append(("REMOTE_LINK", "a pointer at a MISSING dir moves nothing",
                         "NEVER_RUN", nv["klass"], "PASS" if good else "FAIL"))
        finally:
            shutil.rmtree(oog, ignore_errors=True)
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


def run_census(include_out_of_git=True):
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
        ev = classify_case(cr, has_cd, has_tpl, strict=True)
        ev["tree"] = "repo"
        out.append(ev)
    for ev in discover_orphan_run_dirs(territory, [r[0] for r in roots],
                                       strict=True):
        ev["tree"] = "repo"
        out.append(ev)

    # ---- OUT OF GIT.  Roots enumerated from docs/LOCATIONS.md; every
    # top-level store walked so a disagreement between the index and the disk
    # is measured rather than assumed.
    recon = []
    if include_out_of_git:
        recon = reconcile_out_of_git()
        for store in recon:
            if not store["case_roots"]:
                continue
            sroots = store["roots"]
            for cr, has_cd, has_tpl in sroots:
                ev = classify_case(cr, has_cd, has_tpl, strict=False)
                ev["tree"] = "out_of_git"
                ev["store"] = store["root"]
                out.append(ev)
            for ev in discover_orphan_run_dirs([store["root"]],
                                               [r[0] for r in sroots],
                                               strict=False,
                                               prune=OUT_OF_GIT_PRUNE):
                ev["tree"] = "out_of_git"
                ev["store"] = store["root"]
                out.append(ev)

    for ev in out:
        fk = family_key(ev["case_root"])
        ev["family"] = fk
        v = find_verdict(fk, vidx)
        ev["verdict_path"] = v[0] if v else None
        ev["verdict_tokens"] = v[1] if v else []
        ev["graded"] = bool(v)
    return out, recon


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
    ap.add_argument("--repo-only", action="store_true",
                    help="v1 behaviour: repository territory only.  Kept so "
                         "the out-of-git delta can be measured, not asserted.")
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
        rows, recon = run_census(include_out_of_git=not args.repo_only)
    except Refusal as e:
        print(f"\nREFUSING: {e}", file=sys.stderr)
        return 2

    counts = {}
    for r in rows:
        counts[r["klass"]] = counts.get(r["klass"], 0) + 1
    repo_rows = [r for r in rows if r.get("tree") == "repo"]
    oog_rows = [r for r in rows if r.get("tree") == "out_of_git"]

    print("CENSUS -- cfd territory, plus the out-of-git stores")
    print("  unit:      a directory D with D/system/controlDict (case INSTANCE)")
    print("             or D/system/controlDict*.template (case DEFINITION)")
    print("  territory: cases/ minus {RANS_LES_closure_models, dafoam};")
    print("             verification/runs/ minus {T-family, F14-cooling-ladder,")
    print("             THERMAL_K0_runs}; models/")
    if not args.repo_only:
        print("  PLUS:      every top-level store under ~ that holds case roots,")
        print("             enumerated from docs/LOCATIONS.md and reconciled")
        print("             against the disk.  Those stores are LAB-WIDE, not")
        print("             cfd-only: a row's `tree` column says which it is.")
    print(f"  case roots discovered: {len(rows)}"
          f"  (repo {len(repo_rows)}, out-of-git {len(oog_rows)})")
    print()
    print(f"  {'class':<24}{'total':>7}{'repo':>7}{'out_of_git':>12}")
    for k in sorted(counts):
        nr = sum(1 for r in repo_rows if r["klass"] == k)
        no = sum(1 for r in oog_rows if r["klass"] == k)
        print(f"  {k:<24}{counts[k]:>7}{nr:>7}{no:>12}")
    print()

    if not args.repo_only:
        print("OUT-OF-GIT ROOTS -- enumerated from docs/LOCATIONS.md, then "
              "reconciled against the disk")
        print(f"  {'store':<48}{'named?':>8}{'case roots':>12}")
        dis = []
        for s in recon:
            if s["case_roots"] == 0 and not s["named_in_locations"]:
                continue          # nothing there and nothing claimed
            mark = "yes" if s["named_in_locations"] else "NO"
            if s["case_roots"] and not s["named_in_locations"]:
                dis.append(s)
            print(f"  {s['root']:<48}{mark:>8}{s['case_roots']:>12}")
        print(f"  DISAGREEMENTS (holds case roots, NOT named in LOCATIONS.md): "
              f"{len(dis)}")
        for s in dis:
            print(f"    {s['root']}  {s['case_roots']} case roots")
        print()

    never = [r for r in rows if r["klass"] == "NEVER_RUN"]
    cannot = [r for r in rows if r["missing_binary"]]
    print(f"  NEVER_RUN predicate: no solver log with an 'ExecutionTime = ' line,")
    print(f"    no time directory > 0 with content (case level OR processor*/),")
    print(f"    no mesh (constant/polyMesh/points or a mesh-utility log), no")
    print(f"    unattributed time-looping log, and no recorded remote_dir that")
    print(f"    itself shows solve evidence.")
    print(f"  NEVER_RUN case roots: {len(never)}"
          f"  (repo {sum(1 for r in never if r.get('tree') == 'repo')},"
          f" out-of-git {sum(1 for r in never if r.get('tree') == 'out_of_git')})")
    phys = [r for r in rows if r["klass"] == "RAN_PHYSICS_NO_LOG"]
    print(f"  RAN_PHYSICS_NO_LOG predicate: field data written by a time loop, "
          f"and NO solver log.")
    print(f"    rule 4 cannot be certified; 'bookkeeping never voids physics' "
          f"says the fields stand.")
    print(f"  RAN_PHYSICS_NO_LOG case roots: {len(phys)}"
          f"  (of which reach controlDict endTime: "
          f"{sum(1 for r in phys if r.get('endtime_fields'))})")
    link = [r for r in rows if r["klass"] == "RAN_AT_LINKED_REMOTE"]
    print(f"  RAN_AT_LINKED_REMOTE (own artifacts show nothing; the remote_dir "
          f"this case's OWN staging record names does): {len(link)}")
    for r in sorted(link, key=lambda x: x["case_root"]):
        rd = r["remote_dirs"][0]
        print(f"    {_disp(r['case_root'])}")
        print(f"        -> {rd['dir']}  [{rd['klass']}, physics={rd['physics']}, "
              f"bookkeeping={rd['bookkeeping']}]")
        print(f"        record: {_disp(rd['record'])}")
    unat = [r for r in rows if r["klass"] == "RAN_UNATTRIBUTED_LOG"]
    print(f"  RAN_UNATTRIBUTED_LOG (a time loop ran; this script cannot say "
          f"which binary -- out-of-git only): {len(unat)}")
    print(f"  CANNOT_RUN_WITH_OPENFOAM (controlDict application binary absent): "
          f"{len(cannot)}")
    for r in cannot:
        print(f"    {_disp(r['case_root'])}  missing: {r['missing_binary']}")
    print()

    # family rollup
    fam = {}
    for r in rows:
        f = fam.setdefault(r["family"], {"n": 0, "ran": 0, "never": 0, "mesh": 0,
                                         "init": 0, "tpl": 0, "graded": False,
                                         "verdict": None})
        f["n"] += 1
        k = r["klass"]
        if k in ("RAN_PHYSICS_NO_LOG", "RAN_UNATTRIBUTED_LOG",
                 "RAN_AT_LINKED_REMOTE"):
            f["ran"] += 1
        elif k.startswith("RAN"):
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
                print(f"  {_disp(r['case_root'])}   [{r.get('tree', 'repo')}]")
                print(f"      physics={r.get('physics')}  "
                      f"bookkeeping={r.get('bookkeeping')}")
                print(f"      evidence: {_disp(r['evidence_path'])}")

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
            fh.write("# tree=out_of_git rows come from stores enumerated in "
                     "docs/LOCATIONS.md and reconciled against the disk; those "
                     "stores are LAB-WIDE, not cfd-only.\n")
            fh.write("# physics and bookkeeping are INDEPENDENT columns and are "
                     "never folded into the class: ENDTIME_FIELDS/ABSENT is a "
                     "solve whose log is gone, NONE/COMPLETE is a log whose "
                     "fields are gone.\n")
            fh.write("# RESIDUAL LIMIT: an in-repo case whose work happened out "
                     "of git with NO recorded remote_dir is classified on its own "
                     "artifacts alone and can still read NEVER_RUN. Name-matching "
                     "would close that and reintroduce the F1-vs-F17 false "
                     "negative; such rows are adjudicated by hand.\n")
            fh.write("\t".join(TSV_COLUMNS) + "\n")
            for r in sorted(rows, key=lambda x: (x["klass"], x["case_root"])):
                fh.write(_tsv_row(r))
        print(f"\nTSV: {args.tsv}")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"unit": "case root (system/controlDict or controlDict*.template)",
                       "counts": counts,
                       "out_of_git_reconciliation": [
                           {k: v for k, v in s.items() if k != "roots"}
                           for s in recon],
                       "rows": rows}, fh, indent=1)
        print(f"\nJSON: {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
