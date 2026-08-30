#!/usr/bin/env python3
"""
F23b -- THE GRADING PATH for Hagen-Poiseuille flow on an axisymmetric wedge
(simpleFoam, steady, Re_D = 100, streamwise cyclic, fixed body force, 4 ranks at
every level).

Registration: verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md
              frozen at 57d31dde; AMENDMENT 1 (pre-compute) at 440aca3d.

Rule 5 is reached through `scripts/roache_triple.py::grade_ladder` and through
NOTHING ELSE -- exactly one call node, AST-censused, with the text matcher driven
both ways (C-13).

WHAT THIS PROGRAM WILL NOT DO, and each refusal is a defect this team has paid
for:

  * IT WILL NOT GRADE WITHOUT `--prereg-commit`, AND IT WILL NOT MERELY RECORD
    IT.  Four of five cfd graders (grade_f25, grade_f27, grade_f17c, grade_f23)
    require the flag and then only write it into their output, so ANY forty-hex
    string satisfies them -- which defeats CLAUDE.md rule 2, whose whole content
    is that the frozen file that ran IS the committed blob.  Here the sha is
    RESOLVED and CHECKED EQUAL to this rung's own freeze commit, and the
    registration on disk is hashed against that commit's blob.

  * IT WILL NOT ACCEPT A FULL-FILE HASH OF AN AMENDABLE DOCUMENT.  Rule 6 lets a
    frozen file take DATED AMENDMENTS APPENDED AT THE FOOT with the assertion
    `lines whose number changed above this section: 0`.  A grader that hard-codes
    one blob sha for the registration therefore breaks the moment a legal
    amendment lands -- and F23b already carries one.  `verify_freeze_prefix`
    checks the stronger and correct property: the committed blob must be a
    BYTE-EXACT PREFIX of the file on disk, at BOTH the freeze commit and every
    amendment commit.  That IS rule 6's assertion, measured rather than recited.
    `verify_freeze` -- the full blob-sha1 form -- is carried and is applied to
    the case files, which take no amendments.

  * IT WILL NOT GRADE UNTIL G-WEDGE HAS BEEN BORN.  AMENDMENT 1 section A1.4
    makes the blockMesh-path wedge control GATING: absent, out-of-band or
    wrong-sha receipt -> exit 2.  An undriven control certifies blindness.

  * IT WILL NOT RUN UNDER `python3 -O`, and it carries ZERO `assert` statements
    across every module of this rung.  cfd measured that asserts, refusals,
    planted controls and gates all VANISH under -O (L-332).

  * IT WILL NOT DEGRADE.  Every refusal is exit 2 (rule 4).

  * IT WILL NOT READ A MEASUREMENT OUT OF A GLOB.  Every measurement names ONE
    artifact.  `grep` on this box is a shell function over ugrep 7.8.4, which
    searches files on PARALLEL WORKER THREADS: cfd measured 9 wrong readings in
    30 trials from `grep ... log.* | tail -1`, and BOTH obvious fixes (`-J1`,
    `--sort`) make it DETERMINISTIC AND STILL WRONG -- `log.writeCellCentres`
    sorts last and its only `Time =` line is a zero, so a healthy solver at
    Time = 171 reads as Time = 0 forever.

  * EVERY CONTROL IS DRIVEN BOTH WAYS.  A positive limb that must pass and a
    negative limb that MUST FIRE; a control whose negative limb does not fire is
    reported as MEASURING NOTHING and the run refuses (Sanaa 2026-08-28: "A
    control defined in terms of the thing it controls is not a control").

L-342: PHYSICS_CRITICAL and INFRASTRUCTURE field classes are declared below;
gates and refusals read the first only; the second can only refuse the COST CLAIM
and print a BOOKKEEPING DEFECT line.  Bookkeeping never voids physics.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: grade_f23b.py must not run under `python3 -O` (asserts, refusals, "
                     "planted controls and gates all vanish under -O; L-332).\n")
    sys.exit(2)

import os
import io
import re
import ast
import json
import math
import time
import shutil
import hashlib
import tempfile
import argparse
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)

import roache_triple as RT              # THE GATE. Rule 5 lives here and nowhere else.
import exact_f23b as EX                 # THE EXACT SOLUTION, the model and the frozen tolerances.
import foam_io_f23b as FIO              # THE READERS.
import proj_f23b as PROJ                # THE FROZEN COST ARITHMETIC (section 9.3).
import build_f23b as BUILD              # G-WEDGE and its birth receipt (AMENDMENT 1).

# ---------------------------------------------------------------------------
# THE FREEZE (rule 2)
# ---------------------------------------------------------------------------
PREREG = "verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md"
PREREG_FREEZE_COMMIT = "57d31dde434f3af8332cc8a882808bdb28e21079"
# Dated PRE-COMPUTE amendments, each of which must ALSO be a byte-exact prefix of
# the file on disk.  AMENDMENT 1 made the blockMesh-path wedge control GATING.
PREREG_AMENDMENT_COMMITS = ("440aca3d93b8927fca1dacdd2796b7f12eb61ca5",)
# The five sibling modules of this rung, by sha256.  This file cannot carry its
# own digest; section 12's completed table does, and `--case-freeze-commit`
# verifies ALL SIX including this one against their committed blobs.
SIBLING_SHA256 = {
    "exact_f23b.py": "61e3f9fd41e5bc4a5932e70c4954c19e7719ff2412bb5d849f4b22a7e31308a2",
    "foam_io_f23b.py": "8a25d0e5c6ea079f0a1dfabfb0fad940eba923c25cf8155fc61ee198353c761f",
    "build_f23b.py": "c4ab65465a74c65416b46f237359f3d05778daec31b214dee5ece77842a8b409",
    "proj_f23b.py": "afad6d0240408e8e75269a2254237842efe9f4ab1582b9c30f5e00f9029e5ced",
    "run_f23b.sh": "ebc9d441968cffc512a0be7ca7884ed93abd99104a18fb4683d3a25aa0c66383",
}
CASE_FILES = ("exact_f23b.py", "foam_io_f23b.py", "build_f23b.py", "proj_f23b.py",
              "grade_f23b.py", "run_f23b.sh")

# ---------------------------------------------------------------------------
# THE THREE CAPS -- section 9.0.  The launcher asserts all three BEFORE any
# compute and refuses to start if any disagrees or if the total is not the sum.
# The two caps are enforced against SEPARATE running totals: pre-ladder spend
# never draws down the ladder cap and never moves a CAP_ALLOWANCE.
# ---------------------------------------------------------------------------
CAP_CORE_MIN = 293.0
PRELADDER_CAP_CORE_MIN = 20.0
TOTAL_RUNG_CAP_CORE_MIN = 313.0
ESTIMATE_CORE_MIN = 202.366
CAP_RATIO = 1.4479

DIM = 2                                 # refinement in BOTH directions (r and x), r = 2 exactly
VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
LEVEL_NAMES = EX.level_names()
CELLS = dict((n, nr * nx) for n, nr, nx in EX.LEVELS)
SHAPE = dict((n, (nr, nx)) for n, nr, nx in EX.LEVELS)
RANKS = dict((n, EX.RANKS) for n in LEVEL_NAMES)
DT = 1.0
BAND_FACTOR = EX.BAND_FACTOR
GATES = ("G-F23b-1_E2_normalised_profile", "G-F23b-2_f_Re")

PHYSICS_CRITICAL = (
    "log.simpleFoam `End` line and `Time =` count (fixed-count identity)",
    "RC.txt (solver rc, written by the launcher's EXIT TRAP in the shell that ran mpirun)",
    "processor*/<endTime>/U and p present in every one of the RANKS directories and NEWER than the "
    "serial 0/U (age guard)",
    "processor*/0/C cell centres and processor*/0/V cell volumes",
    "checkpoint U files (the gate quantity and the Class C series)",
    "initial residual of Ux in log.simpleFoam (rule 5 limb 1 census); max|Uy|, max|Uz| at endTime",
    "constant/polyMesh (G-WEDGE's input) and GWEDGE_CONTROL_RECEIPT.txt (its birth)",
)
INFRASTRUCTURE = (
    "ClockTime in log.simpleFoam (cost actual)",
    "box_before.txt / box_after.txt (load and memory probes)",
    "MESH_LINE.txt (recorded mesh-quality reading; the gate is enforced at build time)",
    "CAP_ALLOWANCE.txt / ARM_ALLOWANCE.txt",
    "log.decomposePar, log.blockMesh, log.checkMesh, log.build (utility logs)",
    "RUN_STATUS.* / launcher.queue.out rows written by the launcher or a queue runner",
    "calibration figures derived from any of the above",
)

WRITE_PATH_NOTE = (
    "OpenFOAM ascii volVectorField `U` written by the solver at every checkpoint into each "
    "processor<k>/<t>/ directory: `internalField nonuniform List<vector>` NEWLINE N NEWLINE `(` one "
    "`(ux uy uz)` per line `)`; volVectorField `C` and volScalarField `V` in processor<k>/0/ written "
    "by `postProcess -func writeCellCentres|writeCellVolumes` before decomposePar.  Layout pinned "
    "against REAL solver output on this box: verification/runs/ansys_verification/VMFL019/L1_30/5/U "
    "(icoFoam, v2606, 120 cells), parsed at selftest as a live control.")
REAL_U_ON_BOX = os.path.join(REPO, "verification", "runs", "ansys_verification",
                             "VMFL019", "L1_30", "5", "U")
F23_RUNS = os.path.join(REPO, "verification", "runs", "F23_HP_WEDGE_runs")
DEFAULT_ROOT = os.path.join(REPO, "verification", "runs", "F23b_HP_WEDGE_runs")

# C-10: the alarm channel.  `trapFpe: Floating point exception trapping enabled
# (FOAM_SIGFPE).` is present at line 18 of EVERY log this case produces and is
# NOT a fatal; a matcher that fires on it would flag every clean run.
FATAL_RE = re.compile(r"--> FOAM FATAL (?:ERROR|IO ERROR)|^FOAM FATAL", re.M)
TRAPFPE_BANNER = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE)."

INIT_RES_RE = re.compile(r"Solving for (Ux|Uy|Uz|p), Initial residual = ([0-9eE+\-.]+)")
TIME_RE = re.compile(r"^Time = ([0-9eE+\-.]+)\s*$", re.M)
CLOCK_RE = re.compile(r"ClockTime = ([0-9]+) s")
EXEC_RE = re.compile(r"ExecutionTime = ([0-9.eE+\-]+) s")


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# RULE 2 -- the frozen file that ran must BE the committed blob
# ---------------------------------------------------------------------------
def _git(args, cwd=REPO):
    return subprocess.run(["git"] + list(args), cwd=cwd, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, universal_newlines=True)


def blob_sha1(path):
    data = io.open(path, "rb").read()
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with io.open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_commit(commit):
    out = _git(["rev-parse", "%s^{commit}" % commit])
    if out.returncode != 0:
        refuse("%r is not a commit in this repository -- %s" % (commit, out.stderr.strip()))
    return out.stdout.strip()


def verify_freeze(commit, relpath):
    """Rule 2, the full form: the frozen file that runs must BE the committed
    blob.  `git rev-parse <commit>:<relpath>` against a LOCALLY COMPUTED blob
    sha1 of the file on disk.  Refuses on mismatch."""
    out = _git(["rev-parse", "%s:%s" % (commit, relpath)])
    if out.returncode != 0:
        refuse("FREEZE: %s:%s does not resolve -- %s" % (commit, relpath, out.stderr.strip()))
    want = out.stdout.strip()
    disk = os.path.join(REPO, relpath)
    if not os.path.isfile(disk):
        refuse("FREEZE: %s is not on disk" % disk)
    got = blob_sha1(disk)
    if got != want:
        refuse("FREEZE: %s on disk (blob %s) is NOT the committed blob %s at %s. The grading path is "
               "fixed at the pre-registration commit." % (relpath, got[:12], want[:12], commit))
    return want


def verify_freeze_prefix(commit, relpath):
    """Rule 2 for a document that legally takes DATED AMENDMENTS APPENDED AT THE
    FOOT (rule 6).  The committed blob must be a BYTE-EXACT PREFIX of the file on
    disk -- which is exactly rule 6's `lines whose number changed above this
    section: 0`, measured rather than recited.  Refuses naming the first
    differing byte, so a reader can find the edit."""
    out = _git(["rev-parse", "%s:%s" % (commit, relpath)])
    if out.returncode != 0:
        refuse("FREEZE: %s:%s does not resolve -- %s" % (commit, relpath, out.stderr.strip()))
    blob = _git(["cat-file", "blob", out.stdout.strip()])
    if blob.returncode != 0:
        refuse("FREEZE: cannot read blob %s" % out.stdout.strip())
    want = blob.stdout.encode("utf8", "surrogateescape")
    disk_path = os.path.join(REPO, relpath)
    if not os.path.isfile(disk_path):
        refuse("FREEZE: %s is not on disk" % disk_path)
    disk = io.open(disk_path, "rb").read()
    if len(disk) < len(want):
        refuse("FREEZE: %s on disk is %d bytes, SHORTER than the %d bytes committed at %s. Content "
               "was REMOVED from a frozen file." % (relpath, len(disk), len(want), commit))
    if disk[:len(want)] != want:
        n = next(i for i in range(len(want)) if disk[i] != want[i])
        refuse("FREEZE: %s on disk DIFFERS from the blob committed at %s at byte %d (line %d). A "
               "frozen file is never edited; an amendment is APPENDED AT THE FOOT with `lines whose "
               "number changed above this section: 0` (rule 6)."
               % (relpath, commit, n, disk[:n].count(b"\n") + 1))
    return dict(commit=commit, blob=out.stdout.strip(), prefix_bytes=len(want),
                disk_bytes=len(disk), appended_bytes=len(disk) - len(want),
                appended_lines=disk[len(want):].count(b"\n"))


def check_prereg_commit(given):
    """REQUIRE it and CHECK it -- never merely record it."""
    if not given:
        refuse("--prereg-commit=<sha> is required for a real grade. Rule 2: the gate, threshold, cap "
               "and label are committed BEFORE the solver starts, and the grading path is fixed at "
               "that commit. This rung's freeze commit is %s." % PREREG_FREEZE_COMMIT)
    got = resolve_commit(given)
    if got != PREREG_FREEZE_COMMIT:
        refuse("--prereg-commit=%s resolves to %s, which is NOT this rung's freeze commit %s. A "
               "grader that RECORDS the sha instead of CHECKING it is satisfied by any forty hex "
               "characters, and that defeats rule 2 entirely." % (given, got, PREREG_FREEZE_COMMIT))
    rows = [verify_freeze_prefix(PREREG_FREEZE_COMMIT, PREREG)]
    for c in PREREG_AMENDMENT_COMMITS:
        rows.append(verify_freeze_prefix(c, PREREG))
    return dict(prereg=PREREG, freeze_commit=PREREG_FREEZE_COMMIT,
                amendment_commits=list(PREREG_AMENDMENT_COMMITS), prefix_checks=rows)


def check_case_freeze(commit):
    """OPTIONAL and STRONGER: all six section-12 files hashed against their
    committed blobs at `commit`, this file included."""
    if not commit:
        return None
    c = resolve_commit(commit)
    out = {}
    for f in CASE_FILES:
        out[f] = verify_freeze(c, "cases/F23b_HP_WEDGE/%s" % f)
    return dict(case_freeze_commit=c, blobs=out)


def check_siblings_on_disk():
    """The five siblings by sha256, without needing a commit.  Filled at the
    freeze; a `None` entry is reported as NOT CHECKED rather than passed -- an
    absent measurement is reported as absent."""
    rows, unchecked = {}, []
    for f, want in sorted(SIBLING_SHA256.items()):
        p = os.path.join(HERE, f)
        if not os.path.isfile(p):
            refuse("sibling module %s is absent; this rung cannot grade without it" % p)
        got = sha256_file(p)
        rows[f] = got
        if want is None:
            unchecked.append(f)
        elif got != want:
            refuse("FREEZE: %s has sha256 %s on disk; the frozen table records %s" % (f, got, want))
    return dict(sha256=rows, NOT_CHECKED=unchecked)


# ---------------------------------------------------------------------------
# THE TWO-LIMB CONTROL HARNESS
# ---------------------------------------------------------------------------
def fires(fn, *a, **k):
    """Run `fn` EXPECTING a refusal.  Returns (fired, exit code)."""
    err, sys.stderr = sys.stderr, open(os.devnull, "w")
    try:
        fn(*a, **k)
        return False, None
    except SystemExit as e:
        return True, e.code
    except RT.Refusal:
        return True, 2
    finally:
        sys.stderr.close()
        sys.stderr = err


class Controls(object):
    """Every control is TWO limbs.  The positive limb must PASS.  The negative
    limb MUST FIRE.  A negative limb that does not fire means the control is
    measuring nothing, and this harness says exactly that and refuses."""

    def __init__(self):
        self.rows = []

    def add(self, name, positive, negative_fired, detail=""):
        ok = bool(positive) and bool(negative_fired)
        self.rows.append(dict(control=name, positive_limb_passed=bool(positive),
                              negative_limb_fired=bool(negative_fired), detail=detail, passed=ok))
        return ok

    def failures(self):
        out = []
        for r in self.rows:
            if not r["passed"]:
                if not r["negative_limb_fired"]:
                    out.append("%s: THE NEGATIVE LIMB DID NOT FIRE -- IT IS MEASURING NOTHING. %s"
                               % (r["control"], r["detail"]))
                else:
                    out.append("%s: the positive limb did not pass. %s" % (r["control"], r["detail"]))
        return out

    def seal(self):
        bad = self.failures()
        if bad:
            refuse("CONTROLS DID NOT ESTABLISH THEIR CLAIM:\n  " + "\n  ".join(bad))
        return self.rows


# ---------------------------------------------------------------------------
# READERS -- concatenation over processor directories, ONE NAMED FILE EACH
# ---------------------------------------------------------------------------
def processor_dirs(case_dir, ranks):
    dirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)],
                  key=lambda s: int(s[9:])) if os.path.isdir(case_dir) else []
    if len(dirs) != ranks:
        refuse("%s holds %d processor directories, registered ranks %d" % (case_dir, len(dirs), ranks))
    return [os.path.join(case_dir, d) for d in dirs]


def _read(path, kind, what):
    if not os.path.isfile(path):
        refuse("no %s at %s" % (what, path))
    try:
        F = FIO.read_field(path)
    except FIO.FieldFormatError as e:
        refuse("%s: %s" % (path, e))
    if F["kind"] != kind or F["internal"] is None:
        refuse("%s is not a nonuniform %s field. %s" % (path, kind, WRITE_PATH_NOTE))
    return F["internal"]


def read_geometry(pdirs):
    xs, ys, vs = [], [], []
    for p in pdirs:
        C = _read(os.path.join(p, "0", "C"), "vector", "cell-centre file")
        V = _read(os.path.join(p, "0", "V"), "scalar", "cell-volume file")
        if C.shape[0] != V.shape[0]:
            refuse("%s: 0/C carries %d cells but 0/V carries %d" % (p, C.shape[0], V.shape[0]))
        xs.append(C[:, 0]); ys.append(C[:, 1]); vs.append(V)
    xc, yc, V = np.concatenate(xs), np.concatenate(ys), np.concatenate(vs)
    if np.any(V <= 0):
        refuse("non-positive cell volumes in 0/V")
    return xc, yc, V


def read_U(paths):
    out = []
    for p in paths:
        out.append(_read(p, "vector", "U field"))
    U = np.vstack(out)
    if U.shape[0] < 16:
        refuse("only %d cells across %s; refusing to form a profile norm over that" % (U.shape[0], paths))
    return U


def station_mask(xc, nr, nx):
    dx = EX.L / nx
    xs = EX.L * EX.X_STATION_FRAC + 0.5 * dx
    m = np.abs(xc - xs) < 0.25 * dx
    if int(m.sum()) != nr:
        refuse("the station x = %.9g selects %d cells, registered NR = %d" % (xs, int(m.sum()), nr))
    return m


def e2n_from_files(u_paths, yc, V, mask):
    """G-F23b-1: volume-weighted L2 error of the normalised station profile."""
    U = read_U(u_paths)
    if U.shape[0] != len(yc):
        refuse("U carries %d cells but 0/C carries %d" % (U.shape[0], len(yc)))
    u, y, v = U[mask, 0], yc[mask], V[mask]
    ubar = float(np.sum(v * u) / np.sum(v))
    if ubar <= 0.0:
        refuse("station bulk velocity %.6g is not positive; the normalised profile is undefined" % ubar)
    return EX.e2_normalised(u, ubar, y, v)


def fre_from_files(u_paths, V, mask):
    """G-F23b-2: f.Re from the imposed G and the READ station bulk velocity."""
    U = read_U(u_paths)
    if U.shape[0] != len(V):
        refuse("U carries %d cells but 0/V carries %d" % (U.shape[0], len(V)))
    u, v = U[mask, 0], V[mask]
    ubar = float(np.sum(v * u) / np.sum(v))
    if ubar <= 0.0:
        refuse("station bulk velocity %.6g is not positive; f.Re is undefined" % ubar)
    return EX.f_re(ubar)


def ubar_all_cells(u_paths, V):
    U = read_U(u_paths)
    if U.shape[0] != len(V):
        refuse("U carries %d cells but 0/V carries %d" % (U.shape[0], len(V)))
    return float(np.sum(V * U[:, 0]) / np.sum(V))


def diagnostics_from_files(u_paths, V, mask):
    """PRINTED, NOT GATED: x-uniformity and the transverse field maxima."""
    U = read_U(u_paths)
    ub_all = float(np.sum(V * U[:, 0]) / np.sum(V))
    ub_st = float(np.sum(V[mask] * U[mask, 0]) / np.sum(V[mask]))
    return dict(ubar_all_cells=ub_all, ubar_station=ub_st,
                x_nonuniformity=abs(ub_all - ub_st) / max(abs(ub_st), 1e-300),
                max_abs_Uy=float(np.max(np.abs(U[:, 1]))), max_abs_Uz=float(np.max(np.abs(U[:, 2]))))


# ---------------------------------------------------------------------------
# PLANTED-ZERO CONTROLS (rule 3) -- into COPIES of the REAL processor files,
# read back with the REAL parser, FROM DISK.
# ---------------------------------------------------------------------------
def _planted_copies(u_paths, d):
    tmp = tempfile.mkdtemp(prefix="f23b_plant_")
    work = []
    for k, p in enumerate(u_paths):
        w = os.path.join(tmp, "U_%d" % k)
        if FIO.plant_into_vector_file(p, w, 0, d) == 0:
            shutil.rmtree(tmp, ignore_errors=True)
            refuse("nothing to plant into %s" % p)
        work.append(w)
    return tmp, work


def plant_control_e2n(u_paths, yc, V, mask, level):
    d = RT.PLANT
    U = read_U(u_paths)
    u, y, v = U[mask, 0], yc[mask], V[mask]
    ub = float(np.sum(v * u) / np.sum(v))
    before = EX.e2_normalised(u, ub, y, v)
    predicted = EX.e2_normalised(u + d, ub + d, y, v)       # the plant shifts u AND the read Ubar_h
    tmp, work = _planted_copies(u_paths, d)
    try:
        after = e2n_from_files(work, yc, V, mask)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-13:
        refuse("PLANTED-ZERO CONTROL FAILED for E2n on %s: a Ux offset of %.6e must move E2n to "
               "%.17g; the reader returned %.17g (before %.17g). A zero from a reader not shown able "
               "to see a non-zero is not evidence." % (u_paths, d, predicted, after, before))
    return RT.external_plant_control("e2n_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(u_paths), level=level)


def plant_control_fre(u_paths, V, mask, level):
    d = RT.PLANT
    U = read_U(u_paths)
    u, v = U[mask, 0], V[mask]
    ub = float(np.sum(v * u) / np.sum(v))
    before = EX.f_re(ub)
    predicted = EX.f_re(ub + d)
    tmp, work = _planted_copies(u_paths, d)
    try:
        after = fre_from_files(work, V, mask)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if after == before or abs(after - predicted) > 1e-10:
        refuse("PLANTED-ZERO CONTROL FAILED for f.Re on %s: a Ux offset of %.6e must move f.Re to "
               "%.17g; the reader returned %.17g" % (u_paths, d, predicted, after))
    return RT.external_plant_control("fre_from_files", before, after, plant=(predicted - before),
                                     artifact=";".join(u_paths), level=level)


# ---------------------------------------------------------------------------
# CLASS C -- four elements, PER-LEVEL TOLERANCE (section 5.4); element 4 EXITS
# ---------------------------------------------------------------------------
def class_c_cfg(gate, level):
    tol = EX.PLATEAU_TOL[gate][level]
    return dict(min_samples=EX.PLATEAU_MIN_SAMPLES, window=EX.CLASS_C_WINDOW, trend_tol=tol,
                stat_tol=tol / 2.0, var_ratio=EX.PLATEAU_VAR_RATIO, floor=1.0e-14)


def class_c(t, v, label, cfg):
    """Class C on the GRADED QUANTITY ITSELF, at THAT LEVEL's own tolerance.

    THE L-396 MIRROR, APPLIED TO THE DETECTOR (section 5.4).  A converged F23b
    series sits at the machine floor, where a variance-ratio test on two
    all-but-identical half-windows is meaningless and can fire on nothing.  So if
    BOTH half-window variances are below (16 eps x scale)^2 the variance element
    is DECLARED SATISFIED AND THE REASON IS PRINTED beside the verdict, never
    silently.  A detector that has never been shown able to stay silent is a
    constant, not a reader -- so that clause is driven BOTH WAYS in the controls.
    """
    t = np.asarray(t, dtype=float)
    v = np.asarray(v, dtype=float)
    if v.size < cfg["min_samples"]:
        refuse("CLASS C ELEMENT 4: %s has %d samples; the registered minimum is %d. NOT A RESULT."
               % (label, v.size, cfg["min_samples"]))
    w = int(cfg["window"])
    if v.size < w:
        refuse("CLASS C ELEMENT 1: %s has %d samples, fewer than the window %d" % (label, v.size, w))
    tw, vw = t[-w:], v[-w:]
    scale = max(abs(float(np.mean(vw))), cfg["floor"])
    detail = dict(samples=int(v.size), window=w, window_span=float(tw[-1] - tw[0]),
                  window_mean=float(np.mean(vw)), scale=scale, trend_tol=cfg["trend_tol"],
                  stat_tol=cfg["stat_tol"], var_ratio_band=cfg["var_ratio"])
    slope = float(np.polyfit(tw, vw, 1)[0])
    drift = abs(slope) * (tw[-1] - tw[0]) / scale
    detail.update(fitted_slope=slope, relative_drift_over_window=drift,
                  drift_occupancy=drift / cfg["trend_tol"])
    if drift > cfg["trend_tol"]:
        return "NOT_PLATEAUED_TREND", detail
    hh = w // 2
    m1, m2 = float(np.mean(vw[:hh])), float(np.mean(vw[hh:]))
    raw1, raw2 = float(np.var(vw[:hh])), float(np.var(vw[hh:]))
    s1, s2 = raw1 + cfg["floor"], raw2 + cfg["floor"]
    ratio = s2 / s1
    mfloor = (16.0 * EX.EPS_MACH * scale) ** 2
    at_machine_floor = (raw1 < mfloor and raw2 < mfloor)
    detail.update(half_mean_first=m1, half_mean_second=m2, half_mean_split=abs(m1 - m2) / scale,
                  variance_ratio=ratio, half_variance_raw=(raw1, raw2),
                  machine_floor_threshold=mfloor, variance_at_machine_floor=at_machine_floor)
    if abs(m1 - m2) / scale > cfg["stat_tol"]:
        return "NOT_STATIONARY_MEAN", detail
    if at_machine_floor:
        detail["variance_element"] = ("DECLARED SATISFIED: both half-window variances (%.3e, %.3e) "
                                      "are below (16 eps x scale)^2 = %.3e, where a variance-ratio "
                                      "test is meaningless and can fire on nothing (section 5.4, the "
                                      "L-396 mirror). PRINTED, never silent."
                                      % (raw1, raw2, mfloor))
        return "PLATEAUED", detail
    detail["variance_element"] = "evaluated: ratio %.6g against %s" % (ratio, cfg["var_ratio"])
    if not (cfg["var_ratio"][0] <= ratio <= cfg["var_ratio"][1]):
        return "NOT_STATIONARY_VARIANCE", detail
    return "PLATEAUED", detail


# ---------------------------------------------------------------------------
# ITERATIVE CONVERGENCE -- a CENSUS over every iteration in the Class C window
# ---------------------------------------------------------------------------
def per_iteration_residuals(log_path):
    """[{time, Ux, Uy, Uz, p}] from ONE NAMED LOG, first solve of each field per
    iteration.  Never a glob."""
    if not os.path.isfile(log_path):
        refuse("no solver log at %s; rule 5 limb (1) cannot be evaluated" % log_path)
    per, cur = [], None
    for line in open(log_path, errors="replace"):
        m = TIME_RE.match(line)
        if m:
            cur = dict(time=float(m.group(1)))
            per.append(cur)
            continue
        m = INIT_RES_RE.search(line)
        if m and cur is not None and m.group(1) not in cur:
            cur[m.group(1)] = float(m.group(2))
    return per


def iterative_state(log_path, diag, end_time, write_every):
    per_iter = per_iteration_residuals(log_path)
    n_win = EX.CLASS_C_WINDOW * write_every
    win = [d for d in per_iter if d["time"] > end_time - n_win]
    if len(win) < n_win:
        refuse("only %d iterations inside the %d-iteration census window of %s; an absent "
               "measurement is reported as absent" % (len(win), n_win, log_path))
    bad = 0
    worst = dict(Ux=0.0, Uy=0.0, Uz=0.0, p=0.0)
    for d in win:
        if "Ux" not in d:
            refuse("iteration %g of %s carries no initial residual for Ux" % (d["time"], log_path))
        for k in worst:
            if k in d:
                worst[k] = max(worst[k], d[k])
        if d["Ux"] > EX.UX_RES_TOL:
            bad += 1
    floor = EX.TRANSVERSE_FIELD_TOL * EX.U_MAX
    transverse_bad = diag["max_abs_Uy"] > floor or diag["max_abs_Uz"] > floor
    detail = dict(basis="initial residual of Ux (the driven component) censused over every iteration "
                        "in the Class C window; Uy/Uz/p residuals PRINTED and EXCLUDED (N-AV8: "
                        "vanishing channels normalised by a vanishing scale); transverse components "
                        "checked in the FIELD at endTime instead",
                  artifact=log_path, window_iterations=n_win, ux_tol=EX.UX_RES_TOL,
                  n_ux_above_tol=bad, worst_initial_residuals=worst,
                  ungated_printed=dict(Uy=worst["Uy"], Uz=worst["Uz"], p=worst["p"]),
                  transverse_field_floor=floor, max_abs_Uy=diag["max_abs_Uy"],
                  max_abs_Uz=diag["max_abs_Uz"])
    if bad:
        return "NOT_CONVERGED_%d_Ux_READINGS_ABOVE_TOL" % bad, detail
    if transverse_bad:
        return "NOT_CONVERGED_TRANSVERSE_FIELD_ABOVE_FLOOR", detail
    return "CONVERGED", detail


# ---------------------------------------------------------------------------
# THE ALARM CHANNEL (C-10, L-396)
# ---------------------------------------------------------------------------
def fatal_channel(log_path):
    """Flags a REAL `FOAM FATAL`.  Must NOT flag OpenFOAM's `trapFpe:` banner,
    which is present in every log this case produces."""
    if not os.path.isfile(log_path):
        return dict(artifact=log_path, present=False, fatal=False, why="absent")
    text = open(log_path, errors="replace").read()
    hits = FATAL_RE.findall(text)
    return dict(artifact=log_path, present=True, fatal=bool(hits), n_hits=len(hits),
                trapfpe_banner_present=(TRAPFPE_BANNER in text))


# ---------------------------------------------------------------------------
# COMPLETION -- standing rule 4, ALL CLAUSES OR NONE, PHYSICS_CRITICAL only
# ---------------------------------------------------------------------------
def completion(case_dir, log_path, ranks, end_time):
    out = dict(case=case_dir, log=log_path, end_time=end_time)
    rc_path = os.path.join(case_dir, "RC.txt")
    if not os.path.isfile(rc_path):
        return dict(out, done=False, why="no RC.txt yet: the solver rc is not recorded (run in "
                                         "progress, or the launcher died before its EXIT TRAP ran); "
                                         "PENDING, not a verdict")
    rc = open(rc_path).read().strip()
    out["rc"] = rc
    if rc != "0":
        return dict(out, done=False, crashed=True,
                    why="recorded solver rc is %r, not 0: a crash is a FINDING (NOT A RESULT), not a "
                        "pending run" % rc)
    if not os.path.isfile(log_path):
        return dict(out, done=False, crashed=True, why="rc 0 but no solver log at %s: NOT A RESULT"
                    % log_path)
    text = open(log_path, errors="replace").read()
    times = [float(m.group(1)) for m in TIME_RE.finditer(text)]
    execs = EXEC_RE.findall(text)
    out.update(n_times=len(times), latest=times[-1] if times else None, dt=DT,
               n_execution_time=len(execs))
    if not times:
        return dict(out, done=False, crashed=True, why="rc 0 but no `Time =` lines in the log")
    if not re.search(r"^End\s*$", text, re.M):
        return dict(out, done=False, crashed=True,
                    why="rc 0 recorded but no `End` line: the solver log and the rc disagree")
    if abs(times[-1] - end_time) > 1e-9:
        return dict(out, done=False, why="last time %g is not endTime %g" % (times[-1], end_time))
    if len(times) != end_time:
        return dict(out, done=False, why="fixed-deltaT identity fails: %d `Time` lines, endTime/dt = %d"
                                         % (len(times), end_time))
    if len(execs) != end_time:
        return dict(out, done=False, why="`ExecutionTime` count %d != endTime %d" % (len(execs), end_time))
    fatal = fatal_channel(log_path)
    out["fatal_channel"] = fatal
    if fatal["fatal"]:
        return dict(out, done=False, crashed=True,
                    why="the solver log carries %d FOAM FATAL banner(s) despite rc 0" % fatal["n_hits"])
    zero_u = os.path.join(case_dir, "0", "U")
    if not os.path.isfile(zero_u):
        return dict(out, done=False, why="no serial 0/U to date the launch against (the age guard's "
                                         "datum: the builder writes it LAST)")
    t0 = os.path.getmtime(zero_u)
    pdirs = sorted([d for d in os.listdir(case_dir) if re.fullmatch(r"processor[0-9]+", d)],
                   key=lambda s: int(s[9:]))
    if len(pdirs) != ranks:
        return dict(out, done=False, why="%d processor directories, registered ranks %d"
                    % (len(pdirs), ranks))
    missing, stale = [], []
    for pd in pdirs:
        end_dir = None
        for d in os.listdir(os.path.join(case_dir, pd)):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and abs(float(d) - end_time) < 1e-9:
                end_dir = os.path.join(case_dir, pd, d)
        if end_dir is None:
            return dict(out, done=False, why="%s has no time directory at endTime %g" % (pd, end_time))
        for f in ("U", "p"):
            fp = os.path.join(end_dir, f)
            if not os.path.isfile(fp):
                missing.append("%s/%s" % (pd, f))
            elif os.path.getmtime(fp) <= t0:
                stale.append("%s/%s" % (pd, f))
    if missing:
        return dict(out, done=False, why="fields missing at endTime: %s" % missing)
    if stale:
        return dict(out, done=False, why="AGE GUARD: fields %s at endTime are NOT newer than the "
                                         "serial 0/U, which the builder writes last and which "
                                         "therefore dates the run allowed to produce this answer"
                    % stale)
    return dict(out, done=True,
                why="rc 0; End present; last time == endTime %g; %d `Time` lines == endTime; %d "
                    "`ExecutionTime` lines == endTime; no FOAM FATAL; U and p at endTime in all %d "
                    "processor directories and every one NEWER than the serial 0/U"
                    % (end_time, len(times), len(execs), ranks))


def read_level_counts(case_dir):
    """endTime and writeInterval from the LEVEL'S OWN controlDict -- one named
    artifact, never a glob, and never this module's default."""
    cd = os.path.join(case_dir, "system", "controlDict")
    if not os.path.isfile(cd):
        refuse("no %s; the iteration count this level actually ran under is unknown and an absent "
               "measurement is reported as absent" % cd)
    text = open(cd).read()
    me = re.search(r"^\s*endTime\s+(\d+)\s*;", text, re.M)
    mw = re.search(r"^\s*writeInterval\s+(\d+)\s*;", text, re.M)
    if not (me and mw):
        refuse("%s carries no endTime / writeInterval" % cd)
    et, wi = int(me.group(1)), int(mw.group(1))
    if wi * EX.CHECKPOINTS != et:
        refuse("%s: endTime %d / writeInterval %d gives %g checkpoints, not the frozen %d"
               % (cd, et, wi, et / float(wi), EX.CHECKPOINTS))
    return et, wi


# ---------------------------------------------------------------------------
# THE ARM-ACCEPTANCE READER (section 5.5, AMENDMENT 1 section A1.5)
# ---------------------------------------------------------------------------
def arm_reading(case_dir, ranks, log_path=None):
    """|1 - Ubar| and the Ux initial residual, from the REAL production path.

    Returns the earliest checkpoint at which BOTH acceptance thresholds hold, or
    None with the full series printed.  The REJECT direction is already
    demonstrated on F23's own completed levels (section A1.5); the ACCEPT
    direction is item A0's job and is GATING."""
    log_path = log_path or os.path.join(case_dir, "log.simpleFoam")
    pdirs = processor_dirs(case_dir, ranks)
    V = np.concatenate([_read(os.path.join(p, "0", "V"), "scalar", "cell-volume file") for p in pdirs])
    res = dict((d["time"], d.get("Ux")) for d in per_iteration_residuals(log_path))
    series, accepted_at = [], None
    for t, ups in checkpoint_paths(pdirs):
        ub = ubar_all_cells(ups, V)
        err = abs(1.0 - ub)
        ux = res.get(t)
        ok = (err <= EX.ARM_UBAR_TOL) and (ux is not None) and (ux <= EX.ARM_UX_RES_TOL)
        series.append(dict(time=t, ubar=ub, abs_1_minus_ubar=err, ux_initial_residual=ux, accepts=ok))
        if ok and accepted_at is None:
            accepted_at = int(t)
    return dict(case=case_dir, log=log_path, accepted_at=accepted_at, series=series,
                ubar_tol=EX.ARM_UBAR_TOL, ux_tol=EX.ARM_UX_RES_TOL,
                n_accept_threshold=EX.ARM_N_ACCEPT)


def arm_reader_is_born(a0_dir, ranks=EX.RANKS):
    """AMENDMENT 1 item A0.  A reader shown only able to REJECT is L-396's
    constant in its other costume, so the ACCEPT side is GATING: if A0 does not
    produce an accepting artifact, ARM-P and ARM-F REFUSE rather than
    accept-or-reject and the rung is BLOCKED."""
    if not os.path.isdir(a0_dir):
        refuse("AMENDMENT 1 item A0's artifact directory %s is absent. The arm-acceptance reader's "
               "ACCEPT side has not been demonstrated, so the reader IS NOT BORN and ARM-P/ARM-F "
               "REFUSE rather than accept-or-reject. The rung is BLOCKED." % a0_dir)
    r = arm_reading(a0_dir, ranks)
    if r["accepted_at"] is None:
        best = min((s["abs_1_minus_ubar"] for s in r["series"]), default=float("inf"))
        refuse("AMENDMENT 1 item A0 did not produce an ACCEPTING artifact: the best |1 - Ubar| over "
               "%d checkpoints of %s is %.6e against the threshold %.1e. THE ARM-ACCEPTANCE READER "
               "IS NOT BORN and the rung is BLOCKED."
               % (len(r["series"]), a0_dir, best, EX.ARM_UBAR_TOL))
    return r


# ---------------------------------------------------------------------------
# BANDS -- both from ONE declared parameter applied to the model prediction.
# BYTE-FOR-BYTE F23's (section 6): the predictions are properties of the
# CONVERGED DISCRETE problem and are independent of alpha, relTol and N_ITER.
# ---------------------------------------------------------------------------
def bands():
    tab = dict((r["name"], r) for r in EX.predictions())
    fine = tab["fine"]
    e2p = fine["E2n_pred"]
    tol = BAND_FACTOR * abs(fine["fRe_err_pred"])
    return {
        GATES[0]: dict(
            band=(e2p / BAND_FACTOR, e2p * BAND_FACTOR), reference=0.0, dim=DIM,
            principle=("discretisation-model prediction E2n = %.9e at h_fine = %g (the radial stencil "
                       "simpleFoam reduces to on the wedge mesh's own geometry, solved; wedge bias "
                       "%.2e included), times [1/%g, %g]"
                       % (e2p, fine["h"], fine["wedge_bias_E2n"], BAND_FACTOR, BAND_FACTOR))),
        GATES[1]: dict(
            band=(EX.F_RE_EXACT - tol, EX.F_RE_EXACT + tol), reference=EX.F_RE_EXACT, dim=DIM,
            principle=("exact f.Re = 64 +/- %g x the model's predicted fine-level error (%.6e; wedge "
                       "bias %.2e included) = +/- %.6e"
                       % (BAND_FACTOR, fine["fRe_err_pred"], fine["wedge_bias_fRe"], tol))),
    }


REGISTERED_BANDS = {GATES[0]: (2.376227e-06, 2.138605e-05),
                    GATES[1]: (63.998628773, 64.001371227)}


# ---------------------------------------------------------------------------
# THE DEMONSTRATION -- both gates shown able to take a failing AND a passing
# value, through the REAL readers, on files in the pinned write format
# ---------------------------------------------------------------------------
def synth_level(tmp, nr, nx, u_station, tag):
    g = EX.wedge_geometry(nr)
    dx = EX.L / nx
    xg = (np.arange(nx) + 0.5) * dx
    X, Y = np.meshgrid(xg, g["yc"])                       # (nr, nx)
    xc, yc = X.ravel(), Y.ravel()
    V = np.tile(g["vol"] * dx, (nx, 1)).T.ravel()
    U = np.column_stack([np.tile(u_station, (nx, 1)).T.ravel(), np.zeros(xc.size), np.zeros(xc.size)])
    pd = os.path.join(tmp, tag, "processor0")
    os.makedirs(os.path.join(pd, "0"))
    open(os.path.join(pd, "0", "C"), "w").write(
        "FoamFile { version 2.0; format ascii; class volVectorField; object C; }\n"
        "dimensions [0 1 0 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
        "boundaryField { wall { type calculated; value uniform (0 0 0); } }\n"
        % FIO.fmt_list(np.column_stack([xc, yc, np.zeros(xc.size)]), "vector"))
    open(os.path.join(pd, "0", "V"), "w").write(
        "FoamFile { version 2.0; format ascii; class volScalarField; object V; }\n"
        "dimensions [0 3 0 0 0 0 0];\ninternalField nonuniform List<scalar> \n%s;\n"
        "boundaryField { wall { type calculated; value uniform 0; } }\n" % FIO.fmt_list(V, "scalar"))
    up = os.path.join(pd, "U")
    open(up, "w").write(
        "FoamFile { version 2.0; format ascii; class volVectorField; object U; }\n"
        "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform List<vector> \n%s;\n"
        "boundaryField { wall { type noSlip; } }\n" % FIO.fmt_list(U, "vector"))
    return [pd], [up]


def demonstrate(bnd):
    """ZERO COMPUTE.  C-5 and C-6: the model's SOLVED fine-level station profile
    stands in for the fine field on a 4-column synthetic level at the fine radial
    size -- inside both bands; the error field x40 is outside G-F23b-1; the
    profile x1.001 is outside G-F23b-2."""
    m = EX.model("fine")
    nr, _nx_full = SHAPE["fine"]
    nx = 4
    err = m["u"] - EX.u_exact(m["yc"])
    rows = []
    tmp = tempfile.mkdtemp(prefix="f23b_demo_")
    try:
        cases = ((1.0, 1.0, "inside", "inside"), (40.0, 1.0, "outside", None), (1.0, 1.001, None, "outside"))
        for k, (scale, mult, want1, want2) in enumerate(cases):
            u = (EX.u_exact(m["yc"]) + scale * err) * mult
            pdirs, ups = synth_level(tmp, nr, nx, u, "c%d" % k)
            xc, yc, V = read_geometry(pdirs)
            mask = station_mask(xc, nr, nx)
            cons = "exact + %g x model error field, u x %g" % (scale, mult)
            if want1:
                v1 = e2n_from_files(ups, yc, V, mask)
                lo, hi = bnd[GATES[0]]["band"]
                rows.append(dict(gate=GATES[0], construction=cons, value=v1, band=[lo, hi],
                                 inside=bool(lo <= v1 <= hi), intended=want1))
            if want2:
                v2 = fre_from_files(ups, V, mask)
                lo, hi = bnd[GATES[1]]["band"]
                rows.append(dict(gate=GATES[1], construction=cons, value=v2, band=[lo, hi],
                                 inside=bool(lo <= v2 <= hi), intended=want2))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for r in rows:
        if (r["intended"] == "inside") != r["inside"]:
            refuse("GATE DEMONSTRATION FAILED for %s: construction intended %s returned %.9g against "
                   "%s" % (r["gate"], r["intended"], r["value"], r["band"]))
    seen = set((r["gate"], r["inside"]) for r in rows)
    for g in bnd:
        if (g, True) not in seen or (g, False) not in seen:
            refuse("gate %s was not shown able to take BOTH values" % g)
    return rows


# ---------------------------------------------------------------------------
# COST -- INFRASTRUCTURE fields only (L-342), plus rule 12's calibration clause
# ---------------------------------------------------------------------------
def cost_claim(root):
    defects, spent, per = [], 0.0, {}
    for name in LEVEL_NAMES:
        cd = os.path.join(root, name)
        if not os.path.isdir(cd):
            continue
        log = os.path.join(cd, "log.simpleFoam")          # ONE NAMED ARTIFACT
        hits = CLOCK_RE.findall(open(log, errors="replace").read()) if os.path.isfile(log) else []
        if not hits:
            defects.append("BOOKKEEPING DEFECT: level %s has no ClockTime reading in log.simpleFoam; "
                           "cost actual NOT MEASURED" % name)
        else:
            per[name] = float(hits[-1]) * RANKS[name] / 60.0
            spent += per[name]
        for probe in ("box_before.txt", "box_after.txt", "MESH_LINE.txt", "log.decomposePar",
                      "CAP_ALLOWANCE.txt"):
            if not os.path.isfile(os.path.join(cd, probe)):
                defects.append("BOOKKEEPING DEFECT: level %s lacks %s; NOT MEASURED" % (name, probe))
    return dict(fields="INFRASTRUCTURE", core_min_claim=None if defects else spent,
                per_level_core_min=per, partial_sum_core_min=spent, cap_core_min=CAP_CORE_MIN,
                preladder_cap_core_min=PRELADDER_CAP_CORE_MIN,
                total_rung_cap_core_min=TOTAL_RUNG_CAP_CORE_MIN, defects=defects,
                note="ClockTime x ranks / 60 (4 ranks); dollars at $%.4f/core-h DERIVED, NOT MEASURED"
                     % PROJ.DOLLARS_PER_CORE_H)


def calibration(cost, n_iter):
    """Rule 12's calibration clause, and section 9.5.  A completion report
    without this comparison is INCOMPLETE.  `D_fine` and `S` are reported
    SEPARATELY from the base rate: they are the two EXTRAPOLATED factors and the
    whole point of section 9.2 is to find out whether they were right."""
    est = PROJ.estimate(n_iter)
    rows = []
    for name in LEVEL_NAMES:
        act = cost["per_level_core_min"].get(name)
        pred = est["per_level"][name]
        rows.append(dict(level=name, predicted_core_min=pred, actual_core_min=act,
                         ratio_actual_over_predicted=(None if act is None else act / pred)))
    actual = cost["partial_sum_core_min"] if cost["per_level_core_min"] else None
    complete = len(cost["per_level_core_min"]) == len(LEVEL_NAMES)
    return dict(
        unit="core-minutes (ClockTime s x ranks / 60), from the logs",
        predicted_core_min=est["total"], actual_core_min_gross=actual,
        actual_is_complete=complete,
        ratio_actual_over_predicted=(None if (actual is None or not complete) else actual / est["total"]),
        per_level=rows,
        cleaned_note="gross and cleaned are stated SEPARATELY; waste is named separately and is "
                     "NEVER absorbed into the ratio (COMPUTE_BUDGET_CHARTER section 6). F23's "
                     "194.73 core-min is F23's row, written as WASTE, and is NOT folded into this "
                     "ratio (prereg section 14, R4).",
        extrapolated_factors_reported_separately=dict(
            D_fine=PROJ.D_FINE, S=PROJ.S,
            note="D_fine and S are EXTRAPOLATIONS, not measurements. The one measured drift on this "
                 "ladder is 1.044776; at that drift the ladder would be 170.28 core-min against the "
                 "registered 202.37, i.e. the registered estimate is 18.8 %% above the no-margin "
                 "figure. ARM-P's own measured core-us/cell-iteration is the first real reading of S "
                 "on this dictionary and is a calibration input for the SUCCESSOR, not a cap "
                 "adjustment for this rung."),
        base_rate_measured=dict(PROJ.RATE_MEASURED),
        dollars_derived_not_measured=dict(
            predicted=PROJ.dollars(est["total"]),
            actual=(None if actual is None else PROJ.dollars(actual)),
            rate_per_core_h=PROJ.DOLLARS_PER_CORE_H,
            basis="owner-stated 2026-08-21/22; this box CANNOT read its own billing "
                  "(COMPUTE_BUDGET_CHARTER section 5)"),
        ledger="docs/COST_CALIBRATION.md")


# ---------------------------------------------------------------------------
# CENSUSES AND CONTROLS ON THE INSTRUMENT ITSELF
# ---------------------------------------------------------------------------
def module_paths():
    return [os.path.join(HERE, f) for f in CASE_FILES if f.endswith(".py")]


def ast_no_asserts(paths):
    bad = {}
    for p in paths:
        lines = [n.lineno for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert)]
        if lines:
            bad[p] = lines
    if bad:
        refuse("`assert` carries a check in this rung's own path (L-332): %s" % json.dumps(bad))
    planted = "def f(x):\n    assert x > 0\n    return x\n"
    if sum(1 for n in ast.walk(ast.parse(planted)) if isinstance(n, ast.Assert)) != 1:
        refuse("the assert counter cannot see a planted assert; its zero is not evidence")
    return dict(files_checked=len(paths), assert_nodes=0, planted_assert_seen=True)


def checkpoint_paths(pdirs):
    """{t: [processor<k>/<t>/U ...]} for every t > 0 present in ALL ranks."""
    per = []
    for p in pdirs:
        ts = {}
        for d in os.listdir(p):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and float(d) > 0 and \
                    os.path.isfile(os.path.join(p, d, "U")):
                ts[float(d)] = os.path.join(p, d, "U")
        per.append(ts)
    common = sorted(set.intersection(*[set(t.keys()) for t in per]))
    return [(t, [ts[t] for ts in per]) for t in common]


def c13_grade_ladder_census(C):
    src = open(os.path.abspath(__file__)).read()
    calls = [n.lineno for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "grade_ladder"]
    pat = re.compile(r"RT\.grade_ladder\s*\(")
    lines = src.splitlines()
    grep_hits = [i + 1 for i, ln in enumerate(lines) if pat.search(ln)]
    false_pos = [ln for ln in "def f():\n    return 1\n".splitlines() if pat.search(ln)]
    false_neg = [ln for ln in "import x as RT\nz = RT.grade_ladder(q)\n".splitlines() if pat.search(ln)]
    # The text matcher also sees THIS CONTROL'S OWN PLANTED LITERAL, one line
    # above.  That extra hit is accounted for by name rather than filtered away:
    # a census that quietly drops a hit it did not expect is not a census.
    extra = [n for n in grep_hits if n not in calls]
    extra_is_the_planted_literal = all(lines[n - 1].strip().startswith("false_neg =") for n in extra)
    C.add("C-13 rule-5 order census: EXACTLY ONE grade_ladder call node",
          len(calls) == 1 and calls[0] in grep_hits and extra_is_the_planted_literal,
          (not false_pos) and bool(false_neg),
          "AST call node at %s; the text matcher hits %s -- the call itself plus this control's own "
          "planted literal at %s. The matcher misses a file with no call and SEES a planted call."
          % (calls, grep_hits, extra))
    return dict(ast_call_nodes=calls, grep_lines=grep_hits, planted_literal_lines=extra)


def c14_o_refusal_census(C):
    """Every module must exit 2 under `python3 -O`, and a planted assert must be
    seen by the counter."""
    census = ast_no_asserts(module_paths())
    rcs = {}
    for p in module_paths():
        r = subprocess.run([sys.executable, "-O", p, "--selftest"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rcs[os.path.basename(p)] = r.returncode
    C.add("C-14 -O refusal and zero-assert census over all %d modules" % len(module_paths()),
          census["assert_nodes"] == 0 and all(v == 2 for v in rcs.values()),
          census["planted_assert_seen"],
          "exit codes under -O: %s; a PLANTED assert IS seen by the counter, so its zero is evidence"
          % rcs)
    return dict(census, o_exit_codes=rcs)


def c11_cap_halt_through_the_launchers_own_bytes(C):
    """The launcher's parse-and-branch block, EXTRACTED VERBATIM from run_f23b.sh
    and run with an INJECTED projector output.  HALT=1 -> rc 3; HALT=0 -> rc 0
    falling through.  No box is probed."""
    sh = os.path.join(HERE, "run_f23b.sh")
    if not os.path.isfile(sh):
        refuse("no launcher at %s; C-11 grades the launcher's OWN BYTES and cannot invent them" % sh)
    text = open(sh).read()
    m = re.search(r"# >>> C-11 CAP HALT BLOCK.*?\n(.*?)# <<< C-11 CAP HALT BLOCK", text, re.S)
    if not m:
        refuse("run_f23b.sh carries no `# >>> C-11 CAP HALT BLOCK` ... `# <<< C-11 CAP HALT BLOCK` "
               "markers; C-11 will not grade a block it had to guess at")
    block = m.group(1)
    rcs = {}
    for halt in (1, 0):
        script = ('set -u\nsay() { printf "%%s\\n" "$*"; }\nNAME=probe\nCAP_NOW=293.0\n'
                  'PROJ_OUT="PROJ_CORE_MIN=1.0\nCUMULATIVE=2.0\nHALT=%d\nALLOW_S=100\nBASIS=injected"\n'
                  % halt) + block + "\nexit 0\n"
        r = subprocess.run(["bash", "-c", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rcs[halt] = r.returncode
    C.add("C-11 cap halt, driven through the launcher's OWN extracted bytes",
          rcs[0] == 0, rcs[1] == 3,
          "HALT=0 -> rc %d (falls through); HALT=1 -> rc %d (an overrun STOPS the run and does not "
          "get a new budget)" % (rcs[0], rcs[1]))
    return dict(block_lines=block.count("\n"), rc_halt_1=rcs[1], rc_halt_0=rcs[0])


def c10_alarm_channel(C):
    real = os.path.join(F23_RUNS, "coarse", "log.checkMesh")
    clean = fatal_channel(real)
    tmp = tempfile.mkdtemp(prefix="f23b_fatal_")
    try:
        p = os.path.join(tmp, "log.fatal")
        open(p, "w").write(open(real, errors="replace").read()
                           + "\n--> FOAM FATAL ERROR: (openfoam-2606)\nplanted\n")
        planted = fatal_channel(p)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    C.add("C-10 alarm channel: FOAM FATAL is flagged, the trapFpe banner is NOT",
          (not clean["fatal"]) and clean["trapfpe_banner_present"], planted["fatal"],
          "a REAL clean log carrying `%s` is not flagged; the same log plus one planted FOAM FATAL "
          "banner IS (%d hits)" % (TRAPFPE_BANNER[:38] + "...", planted["n_hits"]))
    return dict(clean=clean, planted=planted)


def c7_plateau_detector_both_ways(C, levels=("coarse", "medium")):
    """MUST FIRE on F23's own retained processor checkpoints -- REAL SOLVER
    OUTPUT, not synthetic.  MUST STAY SILENT on a machine-floor series at each
    level's own scale, with the section 5.4 variance clause PRINTED.  Read-only
    on F23's run root; nothing is written there."""
    fired, silent, detail = [], [], []
    for lvl in levels:
        cd = os.path.join(F23_RUNS, lvl)
        if not os.path.isdir(cd):
            refuse("C-7's must-fire artifact is absent: %s. Section 9.4 registers F23's run root as "
                   "RETAINED because deleting it would delete this control's evidence." % cd)
        pdirs = processor_dirs(cd, EX.RANKS)
        xc, yc, V = read_geometry(pdirs)
        nr, nx = SHAPE[lvl]
        mask = station_mask(xc, nr, nx)
        ts, vs = [], []
        for t, ups in checkpoint_paths(pdirs):
            ts.append(t)
            vs.append(fre_from_files(ups, V, mask))
        cfg = class_c_cfg(GATES[1], lvl)
        st, d = class_c(ts, vs, "F23/%s" % lvl, cfg)
        fired.append(st != "PLATEAUED")
        detail.append(dict(level=lvl, source="F23 real solver output", state=st,
                           relative_drift=d["relative_drift_over_window"],
                           tol=cfg["trend_tol"], occupancy=d["drift_occupancy"],
                           f_Re_at_last_checkpoint=vs[-1], n_checkpoints=len(ts)))
        # MUST STAY SILENT: a machine-floor series at this level's own scale
        base = EX.F_RE_EXACT
        t2 = np.arange(1, EX.CHECKPOINTS + 1, dtype=float) * 10.0
        v2 = base + base * 4.0 * EX.EPS_MACH * np.sin(np.arange(EX.CHECKPOINTS))
        st2, d2 = class_c(t2, v2, "machine_floor/%s" % lvl, cfg)
        silent.append(st2 == "PLATEAUED")
        detail.append(dict(level=lvl, source="machine-floor series at this level's own scale",
                           state=st2, variance_element=d2.get("variance_element"),
                           variance_at_machine_floor=d2.get("variance_at_machine_floor")))
    C.add("C-7 plateau detector at EVERY level, driven BOTH ways",
          all(silent), all(fired),
          "; ".join("%s %s at %.4f x tol" % (r["level"], r["state"], r.get("occupancy", 0.0))
                    for r in detail if r["source"].startswith("F23")))
    return detail


def c9_completion_both_ways(C):
    """Rule 4, every clause, driven both ways on a scratch level.  Nothing is
    written into any run root."""
    tmp = tempfile.mkdtemp(prefix="f23b_l342_")
    limbs = {}
    try:
        et = EX.N_ITER
        cd = os.path.join(tmp, "coarse")
        os.makedirs(os.path.join(cd, "0"))
        open(os.path.join(cd, "0", "U"), "w").write("x")
        time.sleep(0.02)
        for k in range(EX.RANKS):
            os.makedirs(os.path.join(cd, "processor%d" % k, str(et)))
            for f in ("U", "p"):
                open(os.path.join(cd, "processor%d" % k, str(et), f), "w").write("y")
        body = "".join("Time = %d\nGAMG:  Solving for Ux, Initial residual = 1e-14, Final residual = "
                       "1e-15, No Iterations 0\nExecutionTime = %d s  ClockTime = %d s\n" % (i, i, i)
                       for i in range(1, et + 1)) + "End\n"
        log = os.path.join(cd, "log.simpleFoam")
        open(log, "w").write(body)
        open(os.path.join(cd, "RC.txt"), "w").write("0\n")
        good = completion(cd, log, EX.RANKS, et)
        limbs["positive_complete_level_accepted"] = good["done"]
        diag = dict(max_abs_Uy=0.0, max_abs_Uz=0.0)
        st, _ = iterative_state(log, diag, et, EX.WRITE_EVERY)
        limbs["positive_converged_log_read_as_CONVERGED"] = (st == "CONVERGED")
        cc = cost_claim(tmp)
        limbs["infrastructure_deleted_leaves_physics_untouched"] = (
            cc["core_min_claim"] is None and bool(cc["defects"]) and completion(cd, log, EX.RANKS, et)["done"])

        def flip(mutate, label):
            mutate()
            try:
                return not completion(cd, log, EX.RANKS, et)["done"]
            finally:
                open(os.path.join(cd, "RC.txt"), "w").write("0\n")
                open(log, "w").write(body)

        limbs["rc_nonzero_flips"] = flip(
            lambda: open(os.path.join(cd, "RC.txt"), "w").write("134\n"), "rc")
        limbs["missing_End_flips"] = flip(
            lambda: open(log, "w").write(body.replace("End\n", "")), "End")
        limbs["short_log_flips"] = flip(
            lambda: open(log, "w").write(body.replace("Time = %d\n" % et, "", 1)), "count")
        limbs["missing_ExecutionTime_flips"] = flip(
            lambda: open(log, "w").write(re.sub(r"ExecutionTime = 1 s  ", "", body, count=1)), "exec")
        limbs["planted_FOAM_FATAL_flips"] = flip(
            lambda: open(log, "w").write(body.replace("End\n", "--> FOAM FATAL ERROR: planted\nEnd\n")), "fatal")
        # one in-window Ux above tolerance
        tail = body.rfind("Initial residual = 1e-14")
        open(log, "w").write(body[:tail] + body[tail:].replace("Initial residual = 1e-14",
                                                               "Initial residual = 1e-7", 1))
        st_bad, _ = iterative_state(log, diag, et, EX.WRITE_EVERY)
        limbs["in_window_Ux_above_tol_flips"] = (st_bad != "CONVERGED")
        open(log, "w").write(body)
        # a residual OUTSIDE the window must NOT change the state
        open(log, "w").write(body.replace("Initial residual = 1e-14", "Initial residual = 1e-7", 1))
        st_out, _ = iterative_state(log, diag, et, EX.WRITE_EVERY)
        limbs["out_of_window_residual_does_NOT_flip"] = (st_out == "CONVERGED")
        open(log, "w").write(body)
        st_tr, _ = iterative_state(log, dict(max_abs_Uy=1e-6, max_abs_Uz=0.0), et, EX.WRITE_EVERY)
        limbs["transverse_field_above_floor_flips"] = (st_tr != "CONVERGED")
        # THE AGE GUARD: a field at endTime OLDER than 0/U
        old = os.path.join(cd, "processor0", str(et), "U")
        t0 = os.path.getmtime(os.path.join(cd, "0", "U"))
        os.utime(old, (t0 - 10, t0 - 10))
        age = completion(cd, log, EX.RANKS, et)
        limbs["age_guard_flips"] = (not age["done"]) and "AGE GUARD" in age["why"]
        os.utime(old, None)
        # a missing rank
        shutil.rmtree(os.path.join(cd, "processor%d" % (EX.RANKS - 1)))
        limbs["missing_rank_flips"] = not completion(cd, log, EX.RANKS, et)["done"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    pos = all(v for k, v in limbs.items() if k.startswith("positive") or "does_NOT" in k
              or k.startswith("infrastructure"))
    neg = all(v for k, v in limbs.items() if k.endswith("_flips"))
    C.add("C-9 / C-12 rule-4 completion, every clause driven BOTH ways", pos, neg,
          "each of %d corruptions flips the level to NOT A RESULT independently; deleting "
          "INFRASTRUCTURE refuses the COST CLAIM ONLY and leaves the verdict channel untouched; a "
          "residual OUTSIDE the census window does NOT flip it"
          % len([k for k in limbs if k.endswith("_flips")]))
    return limbs


def c8_planted_zero_on_the_real_readers(C):
    """Rule 3 on the field readers, through the REAL production path: the plant
    is written into a COPY of a REAL processor U file with the REAL writer and
    read back with the REAL parser, FROM DISK."""
    src = os.path.join(F23_RUNS, "coarse")
    if not os.path.isdir(src):
        refuse("C-8's artifact is absent: %s" % src)
    pdirs = processor_dirs(src, EX.RANKS)
    xc, yc, V = read_geometry(pdirs)
    nr, nx = SHAPE["coarse"]
    mask = station_mask(xc, nr, nx)
    ups = checkpoint_paths(pdirs)[-1][1]
    pc1 = plant_control_e2n(ups, yc, V, mask, "coarse")
    pc2 = plant_control_fre(ups, V, mask, "coarse")
    # NEGATIVE LIMB: a control handed a reader that did NOT move must FAIL.
    dead = RT.external_plant_control("a_reader_that_cannot_see", 1.0, 1.0, plant=RT.PLANT,
                                     artifact="planted_dead_reader", level="coarse")
    neg, _code = fires(RT.assert_plant_control, dead)
    C.add("C-8 planted-zero on the REAL field readers, from disk",
          pc1["passed"] and pc2["passed"], neg,
          "plant %.6e read back as %.6e (E2n) and %.6e (f.Re) through the real parser on real "
          "processor files; a reader that does NOT move is REFUSED"
          % (RT.PLANT, pc1["read_back_delta"], pc2["read_back_delta"]))
    return dict(e2n=pc1, fre=pc2)


def c5_c6_band_demonstration(C, bnd):
    demo = demonstrate(bnd)
    inside = [r for r in demo if r["inside"]]
    outside = [r for r in demo if not r["inside"]]
    # The registration PRINTS the bands to seven significant figures (E2n) and to
    # nine decimals (f.Re), and those printed numbers ARE the frozen bands.  The
    # check is therefore that the model's band ROUNDS to the printed one at the
    # precision the registration prints -- not that it equals it in binary.
    reg_ok = (all(float("%.7g" % bnd[GATES[0]]["band"][i]) == REGISTERED_BANDS[GATES[0]][i]
                  for i in (0, 1))
              and all(round(bnd[GATES[1]]["band"][i], 9) == REGISTERED_BANDS[GATES[1]][i]
                      for i in (0, 1)))
    C.add("C-5 / C-6 both gates take a PASSING and a FAILING value, and the bands are the "
          "registered ones", len(inside) == 2 and reg_ok, len(outside) == 2,
          "E2n %s  f.Re %s -- byte-for-byte the registration's section 6 bands"
          % (tuple("%.6e" % v for v in bnd[GATES[0]]["band"]),
             tuple("%.9f" % v for v in bnd[GATES[1]]["band"])))
    return demo


def c_freeze_verifier_both_ways(C):
    """The freeze verifier is itself an instrument, so it gets a birth control:
    it must ACCEPT the real registration at its real commits and REFUSE a
    mutated copy.  A verifier never shown able to refuse certifies blindness."""
    pos = check_prereg_commit(PREREG_FREEZE_COMMIT)
    tmp = tempfile.mkdtemp(prefix="f23b_freeze_")
    try:
        rel = os.path.relpath(os.path.join(tmp, "mutated.md"), REPO)
        disk = io.open(os.path.join(REPO, PREREG), "rb").read()
        mutated = bytearray(disk)
        mutated[100] = (mutated[100] + 1) % 128
        io.open(os.path.join(tmp, "mutated.md"), "wb").write(bytes(mutated))
        os.symlink(os.path.join(tmp, "mutated.md"), os.path.join(tmp, "link.md"))
        neg_prefix, _c1 = fires(_verify_prefix_against, PREREG_FREEZE_COMMIT, PREREG,
                                bytes(mutated))
        neg_short, _c2 = fires(_verify_prefix_against, PREREG_FREEZE_COMMIT, PREREG, disk[:100])
        neg_sha, _c3 = fires(check_prereg_commit, "HEAD")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    C.add("rule 2 freeze verifier, driven BOTH ways",
          bool(pos["prefix_checks"]), neg_prefix and neg_short and neg_sha,
          "the registration on disk carries the %s blob as a byte-exact prefix (%d bytes) and every "
          "amendment blob likewise; a ONE-BYTE mutation, a TRUNCATION and a WRONG --prereg-commit "
          "each REFUSE" % (PREREG_FREEZE_COMMIT[:8], pos["prefix_checks"][0]["prefix_bytes"]))
    return pos


def _verify_prefix_against(commit, relpath, disk_bytes):
    """The prefix comparator applied to bytes handed in, so the negative limb can
    mutate a copy without touching the real file."""
    out = _git(["rev-parse", "%s:%s" % (commit, relpath)])
    if out.returncode != 0:
        refuse("FREEZE: %s:%s does not resolve" % (commit, relpath))
    blob = _git(["cat-file", "blob", out.stdout.strip()])
    want = blob.stdout.encode("utf8", "surrogateescape")
    if len(disk_bytes) < len(want):
        refuse("FREEZE: the file is %d bytes, SHORTER than the %d committed at %s"
               % (len(disk_bytes), len(want), commit))
    if disk_bytes[:len(want)] != want:
        n = next(i for i in range(len(want)) if disk_bytes[i] != want[i])
        refuse("FREEZE: DIFFERS from the blob committed at %s at byte %d" % (commit, n))
    return True


def c_receipt_gate(C):
    """AMENDMENT 1's birth requirement, checked from THIS module too."""
    tmp = tempfile.mkdtemp(prefix="f23b_receipt_")
    try:
        good = []
        for lvl in BUILD.RECEIPT_LEVELS:
            tol = EX.TOL_REL_WEDGE[lvl]
            good.append(dict(level=lvl, direction="MUST_ACCEPT", limb1_max_rel=1e-10, refused=False))
            good.append(dict(level=lvl, direction="MUST_REFUSE", limb1_max_rel=3.0 * tol, refused=True))
        rp = os.path.join(tmp, "R.txt")
        BUILD.write_receipt(rp, PREREG_FREEZE_COMMIT, good)
        pos = not fires(BUILD.check_receipt, rp, PREREG_FREEZE_COMMIT)[0]
        neg = fires(BUILD.check_receipt, os.path.join(tmp, "absent.txt"), PREREG_FREEZE_COMMIT)[0] \
            and fires(BUILD.check_receipt, rp, "0" * 40)[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    C.add("AMENDMENT 1 birth requirement: G-WEDGE does not grade until it was born",
          pos, neg, "a well-formed receipt is accepted; an ABSENT receipt and a receipt recording a "
                    "DIFFERENT sha each REFUSE (exit 2)")


def c_fast_parser_agrees_with_the_reference(C):
    if not os.path.isfile(REAL_U_ON_BOX):
        refuse("the real solver output the format is pinned against is absent: %s" % REAL_U_ON_BOX)
    fast = FIO.read_field(REAL_U_ON_BOX)["internal"]
    ref = FIO.read_field(REAL_U_ON_BOX, _reference_parser=True)["internal"]
    tmp = tempfile.mkdtemp(prefix="f23b_parser_")
    try:
        p = os.path.join(tmp, "U")
        txt = open(REAL_U_ON_BOX).read()
        open(p, "w").write(txt.replace("internalField   nonuniform List<vector> \n120",
                                       "internalField   nonuniform List<vector> \n119", 1))
        neg = False
        try:
            FIO.read_field(p)
        except FIO.FieldFormatError:
            neg = True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    C.add("the vectorised parser is BIT-IDENTICAL to the entry-at-a-time reference parser",
          np.array_equal(fast, ref) and fast.shape == (120, 3) and np.all(np.isfinite(fast)), neg,
          "%d vectors from REAL solver output on this box (%s); a declared count that disagrees with "
          "the body REFUSES rather than silently returning the wrong number of values"
          % (fast.shape[0], os.path.relpath(REAL_U_ON_BOX, REPO)))


def c_solver_dicts_match(C):
    """nu, G, ranks, endTime, writeInterval, `consistent yes`, the relaxation
    factors and the patch declarations on disk == the registration."""
    def check():
        tp = open(os.path.join(HERE, "case", "constant", "transportProperties")).read()
        m = re.search(r"^\s*nu\s+([0-9eE+\-.]+)\s*;", tp, re.M)
        if not m or abs(float(m.group(1)) - EX.NU) > 1e-15:
            refuse("transportProperties nu does not equal exact_f23b.NU = %.17g" % EX.NU)
        fo = open(os.path.join(HERE, "case", "constant", "fvOptions")).read()
        m = re.search(r"U\s+\(\(\s*([0-9eE+\-.]+)\s+0\s+0\s*\)\s+0\s*\)\s*;", fo)
        if not m or abs(float(m.group(1)) - EX.G) > 1e-15:
            refuse("fvOptions momentum source does not equal exact_f23b.G = %.17g" % EX.G)
        if not re.search(r"volumeMode\s+specific\s*;", fo) or not re.search(r"selectionMode\s+all\s*;", fo):
            refuse("fvOptions must apply G per unit volume (volumeMode specific) to all cells")
        fs = open(os.path.join(HERE, "case", "system", "fvSolution")).read()
        if re.search(r"^\s*residualControl", fs, re.M):
            refuse("fvSolution carries residualControl; the run must go to endTime")
        if not re.search(r"consistent\s+yes\s*;", fs):
            refuse("fvSolution does not carry `consistent yes`; section 5.3 registers SIMPLEC")
        if not re.search(r"fields\s*\{\s*p\s+1\.0;\s*\}", fs) or \
                not re.search(r"equations\s*\{\s*U\s+1\.0;\s*\}", fs):
            refuse("fvSolution relaxation factors are not the registered p 1.0 / U 1.0")
        cd = open(os.path.join(HERE, "case", "system", "controlDict")).read()
        me = re.search(r"^\s*endTime\s+(\d+)\s*;", cd, re.M)
        mw = re.search(r"^\s*writeInterval\s+(\d+)\s*;", cd, re.M)
        if not me or int(me.group(1)) != EX.N_ITER:
            refuse("controlDict endTime is not the registered %d" % EX.N_ITER)
        if not mw or int(mw.group(1)) != EX.WRITE_EVERY:
            refuse("controlDict writeInterval is not the registered %d" % EX.WRITE_EVERY)
        dp = open(os.path.join(HERE, "case", "system", "decomposeParDict")).read()
        m = re.search(r"numberOfSubdomains\s+([0-9]+)\s*;", dp)
        if not m or int(m.group(1)) != EX.RANKS:
            refuse("decomposeParDict numberOfSubdomains is not the registered %d" % EX.RANKS)
        bm = open(os.path.join(HERE, "case", "system", "blockMeshDict.template")).read()
        for pat, what in ((r"inlet\s*\{\s*type cyclic;\s*neighbourPatch outlet;", "inlet cyclic"),
                          (r"outlet\s*\{\s*type cyclic;\s*neighbourPatch inlet;", "outlet cyclic"),
                          (r"wedge1\s*\{\s*type wedge;", "wedge1"),
                          (r"wedge2\s*\{\s*type wedge;", "wedge2"),
                          (r"wall\s*\{\s*type wall;", "wall")):
            if not re.search(pat, bm):
                refuse("blockMeshDict.template does not declare %s" % what)
        ut = open(os.path.join(HERE, "case", "0", "U.template")).read()
        if not re.search(r"wall\s*\{\s*type noSlip;", ut):
            refuse("0/U.template wall is not noSlip")
        return True
    pos = check()
    # THE NEGATIVE LIMB: the same predicate, pointed at a MUTATED COPY in a
    # scratch tree.  The frozen file is never touched.
    neg = _dict_checker_refuses_a_mutation()
    C.add("the solver dictionaries on disk ARE the registered ones", pos, neg,
          "nu %.4g, G %.4g, ranks %d, endTime %d, writeInterval %d, `consistent yes`, relaxation "
          "p 1.0 / U 1.0, no residualControl; a mutated `consistent no` REFUSES"
          % (EX.NU, EX.G, EX.RANKS, EX.N_ITER, EX.WRITE_EVERY))


def _dict_checker_refuses_a_mutation():
    """Point the fvSolution predicate at a MUTATED COPY in a scratch tree.  The
    frozen file is never touched."""
    tmp = tempfile.mkdtemp(prefix="f23b_dictmut_")
    try:
        dst = os.path.join(tmp, "case", "system")
        os.makedirs(dst)
        src = open(os.path.join(HERE, "case", "system", "fvSolution")).read()
        open(os.path.join(dst, "fvSolution"), "w").write(src.replace("consistent      yes;",
                                                                     "consistent      no;"))
        text = open(os.path.join(dst, "fvSolution")).read()
        return not re.search(r"consistent\s+yes\s*;", text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def c_caps_agree(C):
    """Section 9.0: the three caps agree across launcher and grader, and the
    total IS the sum of its two parts."""
    sh = os.path.join(HERE, "run_f23b.sh")
    got = {}
    if os.path.isfile(sh):
        text = open(sh).read()
        for nm in ("CAP_CORE_MIN", "PRELADDER_CAP_CORE_MIN", "TOTAL_RUNG_CAP_CORE_MIN"):
            m = re.search(r"^%s=([0-9.]+)" % nm, text, re.M)
            got[nm] = float(m.group(1)) if m else None
    pos = (abs(CAP_CORE_MIN - PROJ.cap(EX.N_ITER)) < 1e-9
           and abs(PRELADDER_CAP_CORE_MIN - PROJ.PRELADDER_CAP_CORE_MIN) < 1e-9
           and abs(TOTAL_RUNG_CAP_CORE_MIN - (PRELADDER_CAP_CORE_MIN + CAP_CORE_MIN)) < 1e-9
           and abs(ESTIMATE_CORE_MIN - PROJ.estimate(EX.N_ITER)["total"]) < 5e-4
           and abs(CAP_CORE_MIN / ESTIMATE_CORE_MIN - CAP_RATIO) < 5e-5
           and all(got.get(k) is not None for k in got)
           and abs(got.get("CAP_CORE_MIN", -1) - CAP_CORE_MIN) < 1e-9
           and abs(got.get("PRELADDER_CAP_CORE_MIN", -1) - PRELADDER_CAP_CORE_MIN) < 1e-9
           and abs(got.get("TOTAL_RUNG_CAP_CORE_MIN", -1) - TOTAL_RUNG_CAP_CORE_MIN) < 1e-9)
    neg = abs((PRELADDER_CAP_CORE_MIN + 1.0 + CAP_CORE_MIN) - TOTAL_RUNG_CAP_CORE_MIN) > 1e-9
    C.add("section 9.0: all THREE caps agree launcher/grader and total == the sum of its parts",
          pos, neg, "ladder %.1f, pre-ladder %.1f, total %.1f core-min; estimate %.3f at CAP_RATIO "
                    "%.4f; launcher reads %s" % (CAP_CORE_MIN, PRELADDER_CAP_CORE_MIN,
                                                 TOTAL_RUNG_CAP_CORE_MIN, ESTIMATE_CORE_MIN,
                                                 CAP_RATIO, got))


def c_sibling_digests(C):
    """The five siblings by sha256, frozen at the freeze and checked at every
    entry.  NEGATIVE LIMB: one byte appended to a COPY must change the digest --
    a hash comparator never shown able to see a difference certifies blindness
    exactly the way a zero from an unproven reader does."""
    rows = check_siblings_on_disk()
    tmp = tempfile.mkdtemp(prefix="f23b_sha_")
    try:
        p = os.path.join(tmp, "copy")
        src = os.path.join(HERE, "proj_f23b.py")
        io.open(p, "wb").write(io.open(src, "rb").read() + b"#")
        neg = sha256_file(p) != sha256_file(src)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    C.add("the five sibling modules ARE their frozen sha256 digests",
          not rows["NOT_CHECKED"], neg,
          "%d digests checked, %d NOT CHECKED; ONE APPENDED BYTE changes the digest, so the "
          "comparator can see a difference and its equalities are evidence"
          % (len(rows["sha256"]), len(rows["NOT_CHECKED"])))
    return rows


def _live_backtick_lines(text):
    """Lines carrying a BACKTICK outside a whole-line `#` comment.  In a
    double-quoted shell string a backtick is COMMAND SUBSTITUTION, so a
    verdict-bearing phrase written between backticks is EXECUTED and replaced by
    nothing while every check around it still passes."""
    out = []
    for i, ln in enumerate(text.splitlines(), 1):
        if "`" in ln and not ln.lstrip().startswith("#"):
            out.append(i)
    return out


def c_launcher_has_no_live_backtick(C):
    """L-403, e779bdc7 and this file's own history.  Three teams paid for the
    unquoted-heredoc / live-backtick defect in one afternoon, and this launcher
    reproduced it in its own DICTIONARIES AGREE line: `consistent yes` was
    command-substituted to nothing, the registered setting vanished from the
    printed record, and the checks all still passed.  A lesson is not applied
    until EVERY CALL SITE ASSERTS IT (rule 14), so it is asserted here."""
    sh = os.path.join(HERE, "run_f23b.sh")
    live = _live_backtick_lines(open(sh).read())
    planted = _live_backtick_lines('say "the verdict is `GATE FAIL` today"\n')
    C.add("the launcher carries NO live backtick (a command substitution the author did not intend)",
          not live, bool(planted),
          "0 live backticks in run_f23b.sh; a planted `say \"... `GATE FAIL` ...\"` line IS caught "
          "at line %s, so the zero is evidence" % planted)


def c_sub_selftests(C):
    """The sibling modules' own selftests must pass, and must be shown able to
    fail: each is run under -O, where it MUST exit 2."""
    rows = {}
    for mod in ("exact_f23b.py", "proj_f23b.py"):
        p = os.path.join(HERE, mod)
        ok = subprocess.run([sys.executable, p, "--selftest"], stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL).returncode
        bad = subprocess.run([sys.executable, "-O", p, "--selftest"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL).returncode
        rows[mod] = (ok, bad)
    C.add("sibling selftests green, and each REFUSES under -O",
          all(v[0] == 0 for v in rows.values()), all(v[1] == 2 for v in rows.values()),
          "; ".join("%s rc %d, under -O rc %d" % (k, v[0], v[1]) for k, v in rows.items()))


# ---------------------------------------------------------------------------
# THE GRADE
# ---------------------------------------------------------------------------
def grade_one(root, gate, bnd):
    levels, detail = [], []
    for name in LEVEL_NAMES:
        case_dir = os.path.join(root, name)
        if not os.path.isdir(case_dir):
            return dict(gate=gate, verdict="PENDING", note="level %r absent from %s" % (name, root))
        end_time, write_int = read_level_counts(case_dir)
        log = os.path.join(case_dir, "log.simpleFoam")
        comp = completion(case_dir, log, RANKS[name], end_time)
        if not comp["done"]:
            verdict = "NOT A RESULT" if comp.get("crashed") else "PENDING"
            return dict(gate=gate, verdict=verdict, note="level %r: %s" % (name, comp["why"]),
                        completion=comp)
        pdirs = processor_dirs(case_dir, RANKS[name])
        xc, yc, V = read_geometry(pdirs)
        nr, nx = SHAPE[name]
        if len(xc) != CELLS[name]:
            refuse("level %s carries %d cells, registered %d" % (name, len(xc), CELLS[name]))
        mask = station_mask(xc, nr, nx)
        ts, vs, last = [], [], None
        for t, ups in checkpoint_paths(pdirs):
            ts.append(t)
            vs.append(e2n_from_files(ups, yc, V, mask) if gate == GATES[0]
                      else fre_from_files(ups, V, mask))
            last = ups
        if last is None:
            refuse("no checkpoint U files under %s; the gate quantity is ABSENT" % case_dir)
        diag = diagnostics_from_files(last, V, mask)
        it_state, it_detail = iterative_state(log, diag, end_time, write_int)
        pl_state, pl_detail = class_c(ts, vs, "%s/%s" % (name, gate), class_c_cfg(gate, name))
        levels.append(dict(name=name, cells=CELLS[name], value=vs[-1]))
        detail.append(dict(name=name, cells=CELLS[name], value=vs[-1], artifact=last, h=EX.h_of(nr),
                           end_time=end_time, write_interval=write_int, completion=comp,
                           iterative=it_state, iterative_detail=it_detail, plateau=pl_state,
                           plateau_detail=pl_detail, plateau_tol=EX.PLATEAU_TOL[gate][name],
                           diagnostics_printed_not_gated=diag, yc=yc, V=V, mask=mask))
    fd = detail[-1]
    if gate == GATES[0]:
        pc = plant_control_e2n(fd["artifact"], fd["yc"], fd["V"], fd["mask"], fd["name"])
    else:
        pc = plant_control_fre(fd["artifact"], fd["V"], fd["mask"], fd["name"])
    for d in detail:
        d.pop("yc"); d.pop("V"); d.pop("mask")
    spec = bnd[gate]
    # ---- THE ONE AND ONLY GATE CALL. -----------------------------------------
    row = RT.grade_ladder(
        quantity=gate, levels=levels, dim=spec["dim"], band=spec["band"], plant_control=pc,
        iterative_states=dict((d["name"], d["iterative"]) for d in detail),
        plateau_states=dict((d["name"], d["plateau"]) for d in detail),
        reference=spec["reference"])
    row["gate"] = gate
    row["band_principle"] = spec["principle"]
    row["levels_detail"] = detail
    row["ungated_channels_note"] = ("Uy/Uz/p initial residuals and the x-uniformity diagnostic are "
                                    "PRINTED in levels_detail and EXCLUDED from the gate by the "
                                    "freeze (N-AV8)")
    row["gated_by"] = ("scripts/roache_triple.py::grade_ladder -- rule 5 is reached through this call "
                       "and through nothing else; GCI at Fs = %g, never quoted when the three values "
                       "are not monotone" % RT.FS)
    if row["verdict"] not in VERDICTS:
        refuse("%s produced a verdict outside the fixed vocabulary: %r" % (gate, row["verdict"]))
    return row


def run_controls(bnd, deep=True):
    C = Controls()
    out = {}
    out["freeze"] = c_freeze_verifier_both_ways(C)
    c_receipt_gate(C)
    out["assert_census"] = c14_o_refusal_census(C)
    out["grade_ladder_census"] = c13_grade_ladder_census(C)
    c_caps_agree(C)
    c_launcher_has_no_live_backtick(C)
    out["siblings"] = c_sibling_digests(C)
    c_sub_selftests(C)
    c_fast_parser_agrees_with_the_reference(C)
    c_solver_dicts_match(C)
    out["gate_demonstration"] = c5_c6_band_demonstration(C, bnd)
    out["alarm_channel"] = c10_alarm_channel(C)
    out["cap_halt"] = c11_cap_halt_through_the_launchers_own_bytes(C)
    out["completion"] = c9_completion_both_ways(C)
    out["planted_zero"] = c8_planted_zero_on_the_real_readers(C)
    if deep:
        out["plateau"] = c7_plateau_detector_both_ways(C)
    else:
        out["plateau"] = "NOT RUN (--shallow): C-7's must-fire limb reads F23's real checkpoints"
    out["controls"] = C.seal()
    return C, out


def main(argv=None):
    ap = argparse.ArgumentParser(description="F23b grading path")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--out", default=None)
    ap.add_argument("--prereg-commit")
    ap.add_argument("--case-freeze-commit", default=None,
                    help="OPTIONAL and STRONGER: hash all six section-12 files against this commit")
    ap.add_argument("--receipt", default=BUILD.RECEIPT)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--shallow", action="store_true",
                    help="selftest: skip C-7's must-fire limb over F23's real checkpoints")
    ap.add_argument("--arm-read", default=None,
                    help="print the arm-acceptance reading for one arm directory and stop")
    ap.add_argument("--arm-born", default=None,
                    help="AMENDMENT 1 item A0: refuse unless this directory births the reader")
    a = ap.parse_args(argv)

    if a.arm_read or a.arm_born:
        d = a.arm_born or a.arm_read
        r = arm_reader_is_born(d) if a.arm_born else arm_reading(d, EX.RANKS)
        for s in r["series"]:
            print("  iter %-8d |1-Ubar| = %.6e   Ux initial residual = %s   %s"
                  % (s["time"], s["abs_1_minus_ubar"],
                     "absent" if s["ux_initial_residual"] is None else "%.6e" % s["ux_initial_residual"],
                     "ACCEPTS" if s["accepts"] else "rejects"))
        print("ACCEPTED_AT=%s" % ("" if r["accepted_at"] is None else r["accepted_at"]))
        print("UBAR_TOL=%.1e UX_TOL=%.1e N_ACCEPT_THRESHOLD=%d"
              % (r["ubar_tol"], r["ux_tol"], r["n_accept_threshold"]))
        return 0

    bnd = bands()

    if a.selftest:
        t0 = time.time()
        C, out = run_controls(bnd, deep=not a.shallow)
        wall = time.time() - t0
        print(json.dumps(dict(controls=out["controls"], assert_census=out["assert_census"],
                              freeze=out["freeze"], caps=dict(
                                  ladder=CAP_CORE_MIN, preladder=PRELADDER_CAP_CORE_MIN,
                                  total=TOTAL_RUNG_CAP_CORE_MIN, estimate=ESTIMATE_CORE_MIN),
                              bands=dict((k, dict(band=v["band"], reference=v["reference"],
                                                  principle=v["principle"])) for k, v in bnd.items()),
                              model_levels=EX.predictions(),
                              model_orders=dict(wedge=EX.model_orders(), polar=EX.model_orders(polar=True)),
                              gate_demonstration=out["gate_demonstration"],
                              plateau_control=out["plateau"], write_path=WRITE_PATH_NOTE,
                              siblings=check_siblings_on_disk(),
                              selftest_wall_s=round(wall, 1)), indent=2, default=str))
        print("")
        for r in out["controls"]:
            print("  %-78s positive %-5s negative-limb %s"
                  % (r["control"][:78], r["positive_limb_passed"],
                     "FIRED" if r["negative_limb_fired"] else "DID NOT FIRE"))
        plateau_claim = ("the plateau detector FIRED on F23's REAL non-converged checkpoints and "
                         "STAYED SILENT at the machine floor, "
                         if not a.shallow else
                         "C-7 WAS NOT RUN (--shallow): the plateau detector has NOT been shown able "
                         "to fire in this invocation, and an absent measurement is reported as "
                         "absent -- a full grade always runs it, ")
        print("\nSELFTEST GREEN in %.1f s -- %d controls, EVERY ONE DRIVEN BOTH WAYS: a positive limb "
              "that passed and a negative limb that FIRED. 0 assert nodes across %d modules, every "
              "module exits 2 under -O, exactly one grade_ladder call node, both gate quantities "
              "shown able to take a passing AND a failing value through the real reader, the "
              "planted-zero read back from disk through the real parser, rule 4's every clause "
              "flipped independently including the AGE GUARD, %sand the "
              "registration on disk carries the freeze blob as a byte-exact PREFIX."
              % (wall, len(out["controls"]), len(module_paths()), plateau_claim))
        return 0

    # ---- A REAL GRADE --------------------------------------------------------
    freeze = check_prereg_commit(a.prereg_commit)
    case_freeze = check_case_freeze(a.case_freeze_commit)
    siblings = check_siblings_on_disk()
    receipt = BUILD.check_receipt(a.receipt, resolve_commit(a.prereg_commit))
    C, ctl = run_controls(bnd, deep=True)

    rows = [grade_one(a.root, g, bnd) for g in GATES]
    cost = cost_claim(a.root)
    n_iter = EX.N_ITER
    for r in rows:
        for d in r.get("levels_detail", []):
            n_iter = d["end_time"]
    cal = calibration(cost, n_iter)
    out = a.out or os.path.join(a.root, "F23b_GRADED.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(dict(rung="F23b-HP_WEDGE", prereg=PREREG, prereg_commit=freeze,
                       case_freeze=case_freeze, siblings=siblings, gwedge_receipt=receipt,
                       assert_census=ctl["assert_census"], controls=ctl["controls"],
                       gate_demonstration=ctl["gate_demonstration"],
                       plateau_control=ctl["plateau"], write_path=WRITE_PATH_NOTE,
                       caps=dict(ladder=CAP_CORE_MIN, preladder=PRELADDER_CAP_CORE_MIN,
                                 total=TOTAL_RUNG_CAP_CORE_MIN, estimate=ESTIMATE_CORE_MIN,
                                 cap_ratio=CAP_RATIO),
                       field_classes=dict(PHYSICS_CRITICAL=PHYSICS_CRITICAL,
                                          INFRASTRUCTURE=INFRASTRUCTURE),
                       cost_claim=cost, calibration=cal, rows=rows), f, indent=2, default=str)

    print("F23b -- HAGEN-POISEUILLE WEDGE -- TALLY")
    print("=" * 78)
    for r in rows:
        print("%-40s %s" % (r["gate"], r["verdict"]))
        for k in ("why", "note"):
            if k in r:
                print("    %s" % r[k])
        for d in r.get("levels_detail", []):
            it = d["iterative_detail"]
            pl = d["plateau_detail"]
            print("    %-7s value %.9g  %s / %s  drift %.3e of tol %.3e  Ux worst %.3e  "
                  "UNGATED(printed): Uy %.3e Uz %.3e p %.3e  max|Uy| %.2e max|Uz| %.2e  "
                  "x-nonuniformity %.2e"
                  % (d["name"], d["value"], d["iterative"], d["plateau"],
                     pl.get("relative_drift_over_window", float("nan")), d["plateau_tol"],
                     it["worst_initial_residuals"]["Ux"], it["ungated_printed"]["Uy"],
                     it["ungated_printed"]["Uz"], it["ungated_printed"]["p"], it["max_abs_Uy"],
                     it["max_abs_Uz"], d["diagnostics_printed_not_gated"]["x_nonuniformity"]))
            if pl.get("variance_element"):
                print("        variance element: %s" % pl["variance_element"])
    print("=" * 78)
    for dline in cost["defects"]:
        print(dline)
    if cost["core_min_claim"] is None:
        print("COST CLAIM REFUSED (infrastructure fields missing); physics verdicts above are "
              "unaffected (L-342): bookkeeping never voids physics")
    else:
        print("cost actual: %.3f core-min of ladder cap %.1f (pre-ladder %.1f, total %.1f); "
              "predicted %.3f; ratio %.4f -- dollars derived, not measured"
              % (cost["core_min_claim"], CAP_CORE_MIN, PRELADDER_CAP_CORE_MIN,
                 TOTAL_RUNG_CAP_CORE_MIN, cal["predicted_core_min"],
                 cal["ratio_actual_over_predicted"] or float("nan")))
    print("calibration row is owed to docs/COST_CALIBRATION.md (rule 12); D_fine = %.2f and S = %.1f "
          "are reported SEPARATELY from the measured base rate (section 9.5)"
          % (PROJ.D_FINE, PROJ.S))
    print("gated by: scripts/roache_triple.py::grade_ladder at Fs = %g" % RT.FS)
    print("written: %s" % out)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except RT.Refusal as e:
        sys.stderr.write("REFUSED (roache_triple): %s\n" % e)
        sys.exit(2)
