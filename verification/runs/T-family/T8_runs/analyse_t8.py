#!/usr/bin/env python3
"""T8 comparator -- MTT pure-plume self-similarity.  THE GRADING PATH.

Registered by ``docs/campaigns/T-family/T8_PREREGISTRATION.md`` section 11 as
"the comparator -- the grading path, fixed at this commit".  Every constant,
every criterion, every refusal and every exit code below is READ OUT OF THAT
DOCUMENT and the section is cited beside it.  Nothing here was chosen by the
author of this file; where the document is silent this file says so IN ITS
OUTPUT rather than choosing quietly (see PLATEAU_MAX_EXPONENT_DRIFT).

WHY THIS FILE EXISTS AT ALL, stated first because it is the point.  A sibling
rung in this family (K0d) was carried to five frozen amendments with a section
11 freeze set that named a comparator, and asserted that comparator existed,
while no line of it had ever been written.  A pre-registration whose grading
path does not exist is not frozen against anything.  This file is committed
BEFORE OR WITH the document that names it, so that section 11's assertion is
true at the moment it binds.

WHAT THIS FILE REFUSES TO DO (CLAUDE.md rule 4: comparators refuse rather than
degrade).  Exit 2, with the reason, on any of:

  * the freeze set of section 11 not matching its committed blobs;
  * strict completion (CLAUDE.md rule 4) unmet on ANY level;
  * the planted zero of section 9 unseen by the reader;
  * mesh/reader inconsistency (cell counts, plane counts, the r2 = 3*r1
    identity the section 12 S3 extrapolation depends on);
  * the SCALE assertion of section 12 S3 failing against the mesh's own volume.

PATH IDIOM, stated so that a clean ``check_grader_self_blindness.py`` report on
this file is worth something.  ``docs/ansys_verification/
GRADER_BLINDNESS_PROBE_COVERAGE.md`` (committed 3dc99590) measured that the
checker's probe B fires ONLY on ``os.path.join`` and is structurally silent on
``pathlib`` and f-string path construction, so a clean report on a pathlib
comparator "carries zero bits, not fewer bits".  EVERY path in this file is
built with ``os.path.join``; there is no ``pathlib`` import and no f-string
path anywhere.  Probe B can therefore genuinely fire here, and its silence is a
measurement.  Probe B is additionally gated on function naming, so the fixture
constructors are named ``make_synthetic_*`` / ``plant_into_*`` and the readers
``read_*`` / ``resolve_*`` / ``check_*`` -- inside its window on purpose.

PROBE A (the L-322 shape: a grader that cannot represent an outcome its own
rules mandate) is answered structurally rather than by luck: every per-row and
per-level record in this file is built by ONE constructor -- ``new_row()`` and
``new_level()`` -- which always writes the complete key set.  There is no
branch that omits a key another branch reads.

THE RICHARDSON SIGN (section 12 S5).  This file imports NEITHER
``analyse_t1c.py`` NOR ``analyse_t3.py``.  Both compute
``richardson = f_fine + e21/den`` with ``e21 = f_med - f_fine``; the correct
extrapolate is ``f_fine - e21/den``.  Under ruling R1 nothing here is gated on
the extrapolate -- the FINE value is graded -- so the defect could not be
load-bearing even if inherited, but a file written after the defect was
recorded does not inherit it.  ``--selftest`` asserts the correct sign against
a closed-form case (1.16/1.04/1.01 at r = 2 has p = 2 and limit 1.0 exactly)
and asserts the structural identity
``richardson + richardson_parent_convention == 2*f_fine``.

DIMENSIONALITY (VERIFICATION_CHARTER section 3.1: the wrong assumed
dimensionality divides every observed order by exactly 1.5).  This file NEVER
infers the refinement ratio from a cell count.  ``R_REFINE = 2.0`` is the
registered construction of section 5 -- every block's divisions doubled in both
directions -- and the mesh is 2-D (radial x axial), so ``DIM = 2`` and the
cell-count ratio 4 = r**DIM is asserted as a CONSISTENCY CHECK, never used as
the source of r.  Both are printed beside every order.

Usage
-----
    python3 analyse_t8.py --selftest         # no case on disk required
    python3 analyse_t8.py --check-freeze     # section 11 freeze set only
    python3 analyse_t8.py [--root DIR]       # grade

Exit codes are the section 12 S6 contract, answering D522 (this lab's own
comparator once exited 0 on a rung with zero graded rows):

    2  REFUSE -- nothing graded
    1  at least one registered row is GATE FAIL
    3  no GATE FAIL, but fewer than three rows reached the band
       (INCLUDING the zero-graded-rows case; non-zero by construction)
    0  all three registered rows reached the band and all are PASS
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

# ===========================================================================
# REGISTERED CONSTANTS.  Each carries the section of T8_PREREGISTRATION.md it
# is read from.  A constant with no section citation does not belong here.
# ===========================================================================

# -- section 11: the freeze set, hashed at analysis time against HEAD --------
FREEZE_SET = (
    os.path.join("docs", "campaigns", "T-family", "T8_PREREGISTRATION.md"),
    os.path.join("verification", "runs", "T-family", "T8_runs", "build_t8.py"),
    os.path.join("verification", "runs", "T-family", "T8_runs", "analyse_t8.py"),
    os.path.join("verification", "runs", "T-family", "T8_runs", "run_one_t8.sh"),
)

# -- section 1: geometry and reference state --------------------------------
D_SOURCE = 0.2                   # m
R_DOMAIN = 12.0 * D_SOURCE       # m   = 2.4
H_DOMAIN = 40.0 * D_SOURCE       # m   = 8.0
TREF = 300.0                     # K
BETA = 1.0 / 300.0               # 1/K
G_ACCEL = 9.81                   # m/s2
WEDGE_FULL_DEG = 5.0             # section 1: axisymmetric 5 deg wedge

# section 12 S3: SCALE = 2*pi/sin(5 deg) converts the flat-sided wedge to the
# full annulus.  THE FORMULA GOVERNS, NOT THE DISPLAYED DECIMAL.  The document
# prints "= 72.0928"; the formula gives 72.09147.  That displayed value is a
# rounding error of 1.85e-5 relative -- larger than the 1e-6 assertion
# tolerance registered in the same sentence -- so using the printed decimal
# would make the comparator refuse every correct mesh.  This file uses the
# formula, and the discrepancy is reported to the supervisor rather than
# silently absorbed.  The formula is also derivable: the flat-sided sector
# between r1 and r2 at half-angle th has area sin(th)cos(th)(r2^2 - r1^2), so
# the full-annulus scale is pi/(sin(th)cos(th)) == 2*pi/sin(2*th).  --selftest
# asserts the two forms agree to 1e-12.
WEDGE_HALF_RAD = math.radians(WEDGE_FULL_DEG / 2.0)
SCALE = 2.0 * math.pi / math.sin(math.radians(WEDGE_FULL_DEG))
SCALE_REL_TOL = 1.0e-6           # section 12 S3: "refuses on disagreement > 1e-6"

# -- section 3 and 4: the graded rows ---------------------------------------
BAND_HALF_WIDTH = 0.05           # section 4: "+/-0.05 absolute on each exponent"
ROWS = ("n_w", "n_T", "n_Q")     # section 3, in the document's own order
EXACT = {"n_w": -1.0 / 3.0, "n_T": -5.0 / 3.0, "n_Q": +5.0 / 3.0}
# section 7 criterion (1): "the field the exponent is built from"
SOURCE_FIELD = {"n_w": "U", "n_T": "T", "n_Q": "U"}

# -- section 4: the fit window and the registered station set ---------------
STATIONS_ZD = tuple(10.0 + 0.5 * i for i in range(31))       # 31 stations
C5_STATIONS_ZD = tuple(10.0 + 0.5 * i for i in range(41))    # section 9 C5, 41
C5_DISCLOSE_DELTA = 2.0 * BAND_HALF_WIDTH                    # "one band width"

# -- section 5: the ladder --------------------------------------------------
LEVELS = ("c", "m", "f")
R_REFINE = 2.0                   # section 5: "ratio r = 2 exactly in BOTH directions"
DIM = 2                          # radial x axial; NEVER inferred from cell counts
FS = 1.25                        # section 5: "GCI at Fs = 1.25"

# -- section 7: strict completion (CLAUDE.md rule 4) ------------------------
FIELDS_REQUIRED = ("T", "U", "p_rgh", "alphat", "nut", "k", "epsilon")
CONV_REL_TOL = 1.0e-6            # "last-two-checkpoint relative change <= 1e-6"

# ---------------------------------------------------------------------------
# THE ONE PLACE THIS PRE-REGISTRATION IS THIN, AND IT IS NOT PAPERED OVER.
#
# Section 7 criterion (1) reads, in full:
#
#     "all three levels iteratively converged -- last-two-checkpoint relative
#      change <= 1e-6 on the field the exponent is built from -- and
#      plateaued; else NOT A RESULT"
#
# The em-dash clause defines "iteratively converged" and this file implements
# it exactly (see check_iterative_convergence).  The trailing conjunct "and
# plateaued" is the wording of CLAUDE.md rule 5 clause (1) carried through, and
# T8 registers NO separate content for it: "plateau" appears exactly once in
# the whole document, at that word, with no threshold, no instrument and no
# per-level criterion.  The two in-lab readings differ --
#
#   * analyse_e4a.py:346 treats "iteratively converged/plateaued" as ONE
#     condition and implements a single last-two-checkpoint test;
#   * analyse_t1b_L4.py:225 treats the plateau as a SEPARATE spatial test
#     (station spread above 0.2 x band across 60/70/80 D),
#
# -- and the T1b reading is inapplicable here by construction: T8's graded
# quantities are POWER LAWS in z and are not supposed to stop varying with z.
# The one T8 instrument that would test the power law's straightness across the
# window is control C5, which section 9 EXPLICITLY bars from gating.
#
# ansys-verification's VMFL051 lesson, made binding on this lane, requires the
# plateau to be checked "level by level, against that level's own registered
# criterion".  T8 has no such criterion, so this file DOES NOT INVENT ONE.  It
# implements clause (1) as the em-dash definition alone, PRINTS that fact
# beside every level, and leaves the hook below for the supervisor's ruling.
# Set it to a float (a maximum permitted relative drift of the fitted exponent
# between the last two checkpoints) and the separate plateau test activates.
# Leaving it None is a decision recorded in the output, not a silent default.
# ---------------------------------------------------------------------------
PLATEAU_MAX_EXPONENT_DRIFT = None

# -- section 8: cost, caps, and the timeout derivation ----------------------
RANKS = 1                        # section 6 R5: serial, nProcs = 1
PREDICTED_CORE_MIN = {"c": 7.13, "m": 42.81, "f": 285.40}
CAP_CORE_MIN = {"c": 15, "m": 80, "f": 500}
# section 8: "the cap is enforced as timeout = cap_core_min * 60 / ranks"
REGISTERED_TIMEOUT_S = {"c": 900, "m": 4800, "f": 30000}

# -- section 9: the planted zero (CLAUDE.md rule 3) -------------------------
PLANT = 1.234e-03                # K, and m/s for the U_z arm
PLANT_TOL = 1.0e-9               # section 9: "tolerance 1e-9 K"

# -- section 9: the registered controls -------------------------------------
C1_AMBIENT_FRACTION = 0.01       # C1: ambient dT < 1 % of centreline, GATES
C2_FLUX_TOL = 0.05               # C2: F conserved to < 5 %, REPORT ONLY
ALPHA_PUBLISHED = (0.11, 0.13)   # section 3 / P1: report-only range

VERDICT_PASS = "PASS"
VERDICT_FAIL = "GATE FAIL"
VERDICT_NAR = "NOT A RESULT"


# ===========================================================================
# refusal
# ===========================================================================
def refuse(msg):
    print("")
    print("REFUSE (exit 2): " + msg)
    print("Nothing is graded.  CLAUDE.md rule 4: comparators refuse rather "
          "than degrade.")
    sys.exit(2)


# ===========================================================================
# section 11 -- the freeze set, hashed against the committed blob
# ===========================================================================
def check_freeze_set(repo=REPO):
    """Hash each freeze-set file on disk against its blob at HEAD.

    CLAUDE.md rule 2, third clause: "verify the frozen file IS the file that
    ran by hashing it against the committed blob".  There is no override and
    no --allow-uncommitted flag: an uncommitted pre-registration is not frozen,
    and grading against an unfrozen document is the defect this rung exists to
    avoid.  Returns (ok, [lines]).
    """
    lines, ok = [], True
    for rel in FREEZE_SET:
        path = os.path.join(repo, rel)
        if not os.path.isfile(path):
            lines.append("  MISSING ON DISK   " + rel)
            ok = False
            continue
        disk = subprocess.run(["git", "hash-object", path], cwd=repo,
                              capture_output=True, text=True)
        head = subprocess.run(["git", "rev-parse", "HEAD:" + rel], cwd=repo,
                              capture_output=True, text=True)
        if disk.returncode != 0:
            lines.append("  CANNOT HASH       " + rel)
            ok = False
        elif head.returncode != 0:
            lines.append("  NOT COMMITTED     " + rel)
            ok = False
        elif disk.stdout.strip() != head.stdout.strip():
            lines.append("  DIFFERS FROM HEAD " + rel +
                         "  disk " + disk.stdout.strip()[:12] +
                         "  HEAD " + head.stdout.strip()[:12])
            ok = False
        else:
            lines.append("  frozen  " + disk.stdout.strip()[:12] + "  " + rel)
    return ok, lines


# ===========================================================================
# OpenFOAM field reading -- standard library only
# ===========================================================================
def read_internal(path, vector=False):
    """Read an OpenFOAM internalField.  Uniform and nonuniform both handled."""
    if not os.path.isfile(path):
        return None
    txt = open(path, errors="replace").read()
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*\n?"
                  r"(\d+)\s*\(", txt)
    if not m:
        m2 = re.search(r"internalField\s+uniform\s+([^;]+);", txt)
        if not m2:
            return None
        v = m2.group(1).strip()
        if v.startswith("("):
            return [tuple(float(x) for x in v.strip("()").split())]
        return [float(v)]
    n = int(m.group(2))
    body = txt[m.end():]
    if vector:
        vals = re.findall(r"\(([^)]*)\)", body)[:n]
        return [tuple(float(x) for x in v.split()) for v in vals]
    vals = re.findall(r"[-0-9.eE+]+", body)[:n]
    return [float(v) for v in vals]


def _substitute_internal(text, values, vector):
    """Return `text` with its nonuniform internalField replaced by `values`."""
    kind = "vector" if vector else "scalar"
    pat = re.compile(r"(internalField\s+nonuniform\s+List<" + kind +
                     r">\s*\n?)(\d+)(\s*\()(.*?)(\)\s*;)", re.S)
    m = pat.search(text)
    if not m:
        return None
    if vector:
        body = "\n".join("(%.16g %.16g %.16g)" % v for v in values)
    else:
        body = "\n".join("%.16g" % v for v in values)
    return text[:m.start()] + m.group(1) + str(len(values)) + m.group(3) + \
        "\n" + body + "\n" + m.group(5) + text[m.end():]


def write_internal(src_path, dst_path, values, vector=False):
    """Copy src to dst with its internalField replaced.  Used ONLY by the
    planted-zero control, and only ever into a temporary directory."""
    txt = open(src_path, errors="replace").read()
    out = _substitute_internal(txt, values, vector)
    if out is None:
        return False
    with open(dst_path, "w") as fh:
        fh.write(out)
    return True


# ===========================================================================
# case-level readers
# ===========================================================================
def read_case_txt(case, key):
    """One value from the CASE.txt build_t8.py wrote beside the case."""
    path = os.path.join(case, "CASE.txt")
    if not os.path.isfile(path):
        return None
    for line in open(path, errors="replace"):
        parts = line.split()
        if len(parts) >= 2 and parts[0] == key:
            return parts[1]
    return None


def resolve_time_dirs(case):
    """Every time directory in the case, ascending by float value.

    RESOLVED BY SCANNING THE DISK, never by formatting a constant into a name.
    That is the L-321 defect (a fixture and a reader sharing one wrong
    assumption about how OpenFOAM spells a time): analyse_f5b_physics.py
    matched "21.9440" while OpenFOAM had written "21.944", and every selftest
    passed because the fixture spelled it the same wrong way.
    """
    if not os.path.isdir(case):
        return []
    out = []
    for d in os.listdir(case):
        if re.fullmatch(r"\d+(\.\d+)?", d) and os.path.isdir(
                os.path.join(case, d)):
            out.append(d)
    return sorted(out, key=float)


def resolve_end_time_dir(case, end_time):
    """The time directory that IS endTime, or None."""
    for d in resolve_time_dirs(case):
        if abs(float(d) - float(end_time)) < 1e-9:
            return d
    return None


def read_status(case_root, level):
    """The STATUS file run_one_t8.sh wrote.  Section 7: rc is RECORDED, never
    inferred from the log."""
    path = os.path.join(case_root, "STATUS.T8_MTT_" + level)
    if not os.path.isfile(path):
        return None
    out = {}
    for line in open(path, errors="replace"):
        if "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip()
    return out


# ===========================================================================
# section 7 -- strict completion (CLAUDE.md rule 4), every clause
# ===========================================================================
def new_level(level):
    """THE ONLY constructor for a per-level record.  Probe A (the L-322 shape)
    is answered structurally: every key exists on every path, always."""
    return dict(level=level, case=None, end_time=None, end_dir=None,
                prev_dir=None, complete=False, reason="not checked",
                clauses=[], rc=None, core_min=None, wall_s=None,
                ranks=None, timeout_s=None, n_cells=None,
                conv={}, planes=None, mesh=None)


def check_completion(case, level, case_root):
    """All clauses of CLAUDE.md rule 4.  Returns (ok, reason, clause_lines).

    Returns rather than exits so that --selftest can plant each failure and
    require this function to see it.  A completion checker never shown able to
    fire is not evidence (standing rule 3, applied to the checker itself).
    """
    cl = []

    def note(name, good, detail):
        cl.append(("PASS" if good else "FAIL", name, detail))
        return good

    if not os.path.isdir(case):
        return False, "case directory absent: " + case, cl

    # -- registered endTime, from the case's own controlDict AND CASE.txt ----
    cd = os.path.join(case, "system", "controlDict")
    if not os.path.isfile(cd):
        return False, "no system/controlDict", cl
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(cd).read(), re.M)
    if not m:
        return False, "controlDict has no endTime", cl
    end_time = float(m.group(1))
    ct = read_case_txt(case, "endTime")
    if ct is None or abs(float(ct) - end_time) > 1e-9:
        return False, ("CASE.txt endTime %s disagrees with controlDict %g"
                       % (ct, end_time)), cl
    note("endTime agrees between controlDict and CASE.txt", True, "%g" % end_time)

    # -- clause: rc = 0, RECORDED to a STATUS file, not inferred from the log -
    st = read_status(case_root, level)
    if st is None:
        return False, "no STATUS file for level " + level, cl
    if "rc" not in st:
        return False, "STATUS file records no rc", cl
    if not note("rc = 0 (recorded, not inferred)", st["rc"] == "0",
                "rc=" + st["rc"]):
        return False, "rc = " + st["rc"] + " (a run that did not return 0 is " \
                      "not done)", cl

    # -- clause: ranks == 1, asserted explicitly (section 6 R5) --------------
    if not note("ranks == 1", st.get("ranks") == "1", "ranks=" + str(st.get("ranks"))):
        return False, "STATUS records ranks=%s; section 6 registers 1" % st.get("ranks"), cl
    npx = read_case_txt(case, "nProcs")
    if not note("CASE.txt nProcs == 1", npx == "1", "nProcs=" + str(npx)):
        return False, "CASE.txt nProcs=%s; section 6 registers 1" % npx, cl
    procdirs = [d for d in os.listdir(case) if d.startswith("processor")]
    if not note("no processor* directories", not procdirs, str(procdirs)):
        return False, "case was decomposed; section 6 registers no decomposition", cl

    # -- clause: the cap instrument is the registered one --------------------
    want_to = CAP_CORE_MIN[level] * 60 // RANKS
    if not note("timeout = cap_core_min * 60 / ranks",
                str(st.get("timeout_s")) == str(want_to) ==
                str(REGISTERED_TIMEOUT_S[level]),
                "timeout_s=%s want=%d registered=%d"
                % (st.get("timeout_s"), want_to, REGISTERED_TIMEOUT_S[level])):
        return False, "the cap instrument is not the registered one", cl

    # -- clause: an End line in log.solve ------------------------------------
    log = os.path.join(case, "log.solve")
    if not os.path.isfile(log):
        return False, "no log.solve", cl
    txt = open(log, errors="replace").read()
    if not note("End line present", re.search(r"^End\s*$", txt, re.M) is not None,
                ""):
        return False, "log.solve has no End line", cl

    # -- clause: ExecutionTime line count == endTime -------------------------
    n_exec = len(re.findall(r"^ExecutionTime\s*=", txt, re.M))
    if not note("ExecutionTime count == endTime", n_exec == int(round(end_time)),
                "count=%d endTime=%g" % (n_exec, end_time)):
        return False, ("ExecutionTime count %d != endTime %g -- the run did "
                       "not take the registered number of steps"
                       % (n_exec, end_time)), cl

    # -- clause: last time == endTime ---------------------------------------
    times = resolve_time_dirs(case)
    if not times:
        return False, "no time directories", cl
    if not note("last time == endTime",
                abs(float(times[-1]) - end_time) < 1e-9,
                "last=%s endTime=%g" % (times[-1], end_time)):
        return False, ("last time %s != endTime %g" % (times[-1], end_time)), cl
    end_dir = times[-1]

    # -- clause: the registered field set present at endTime ----------------
    missing = [f for f in FIELDS_REQUIRED
               if not os.path.isfile(os.path.join(case, end_dir, f))]
    if not note("registered fields present at endTime", not missing,
                "required=" + " ".join(FIELDS_REQUIRED)):
        return False, "fields missing at endTime: " + " ".join(missing), cl

    # -- clause: THE AGE GUARD ----------------------------------------------
    # Every field at endTime NEWER than the case's own 0/T.  0/T is touched
    # LAST at launch by run_one_t8.sh, so it dates the run that was ALLOWED to
    # produce this answer.  A field older than it came from somewhere else.
    zt = os.path.join(case, "0", "T")
    if not os.path.isfile(zt):
        return False, "no 0/T -- the age guard has no datum", cl
    t0 = os.path.getmtime(zt)
    stale = [f for f in FIELDS_REQUIRED
             if os.path.getmtime(os.path.join(case, end_dir, f)) <= t0]
    if not note("age guard: every endTime field newer than 0/T", not stale,
                "0/T mtime=%.3f" % t0):
        return False, ("age guard FAILED -- not newer than 0/T: " +
                       " ".join(stale)), cl

    # -- two checkpoints, which criterion (1) needs --------------------------
    nz = [t for t in times if float(t) != 0.0]
    if not note("two written checkpoints on disk", len(nz) >= 2,
                "checkpoints=" + " ".join(nz)):
        return False, ("only %d checkpoint(s); section 7 criterion (1) needs "
                       "two" % len(nz)), cl

    return True, "complete", cl


# ===========================================================================
# section 7 criterion (1) -- iterative convergence
# ===========================================================================
def check_iterative_convergence(case, field, tol=CONV_REL_TOL):
    """The lab's last-two-written-checkpoints gate, at T8's registered 1e-6.

    NORM, stated because section 7 fixes the tolerance and not the norm.  This
    is the lab's own standing norm for the phrase "last-two-checkpoint
    relative change", carried by analyse_t1c.iterative_convergence (line 197,
    tol 1e-6) and reused by analyse_t1b_L4 and analyse_t9a:

        rel = max_cells |a - b| / (max(b) - min(b))

    T8 uses that phrase and that tolerance verbatim, so this is the registered
    term's established meaning in this lab, not a choice made here.  The code
    is REIMPLEMENTED rather than imported: section 12 S5 bars importing
    analyse_t1c.py and analyse_t3.py.

    For the vector field U the test is applied to BOTH the z-component (the
    component the exponents are built from) AND the worst of all three
    components, and both must pass.  That is strictly stronger than either
    reading alone and can only move a row toward NOT A RESULT, which CLAUDE.md
    rule 5 permits; it can never move one toward PASS.
    """
    times = [t for t in resolve_time_dirs(case) if float(t) != 0.0]
    if len(times) < 2:
        return dict(state="UNJUDGED", rel=None, tol=tol,
                    why="fewer than two checkpoints", between=None)
    vector = (field == "U")
    a = read_internal(os.path.join(case, times[-2], field), vector=vector)
    b = read_internal(os.path.join(case, times[-1], field), vector=vector)
    if a is None or b is None:
        return dict(state="UNJUDGED", rel=None, tol=tol,
                    why="cannot read " + field, between=(times[-2], times[-1]))
    if len(a) != len(b):
        return dict(state="UNJUDGED", rel=None, tol=tol,
                    why="checkpoint sizes differ", between=(times[-2], times[-1]))
    if vector:
        rels = []
        for comp in (2, 0, 1, 2):
            av = [x[comp] for x in a]
            bv = [x[comp] for x in b]
            dmax = max(abs(x - y) for x, y in zip(av, bv))
            rng = max(bv) - min(bv)
            rels.append(dmax / rng if rng > 0 else 0.0)
        rel = max(rels)
    else:
        dmax = max(abs(x - y) for x, y in zip(a, b))
        rng = max(b) - min(b)
        rel = dmax / rng if rng > 0 else 0.0
    return dict(state="CONVERGED" if rel <= tol else "NOT_CONVERGED",
                rel=rel, tol=tol, why="", between=(times[-2], times[-1]))


# ===========================================================================
# the mesh, read from the mesh -- never reconstructed from the build script
# ===========================================================================
def foam(case, cmd):
    """Run an OpenFOAM utility with the registered environment sourced."""
    full = ("source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null "
            "2>&1 && cd " + case + " && " + cmd)
    return subprocess.run(["bash", "-c", full], capture_output=True, text=True)


def ensure_cell_geometry(case, end_dir):
    """Cx, Cy, Cz and V at endTime, WRITTEN BY OPENFOAM FROM THE MESH.

    Deliberately not computed from build_t8.py's block table: a reader that
    reconstructs the mesh from the same source the mesh was built from shares
    one assumption with it and their agreement carries no information (the
    L-321 shape).  Called only AFTER the age guard has been applied, so that
    these newly written files cannot participate in it.
    """
    need = [n for n in ("Cx", "Cy", "Cz", "V")
            if not os.path.isfile(os.path.join(case, end_dir, n))]
    if not need:
        return True, "already present"
    for func in ("writeCellCentres", "writeCellVolumes"):
        r = foam(case, "postProcess -func " + func + " -time " + end_dir +
                 " > log." + func + " 2>&1")
        if r.returncode != 0:
            return False, func + " failed (rc=%d)" % r.returncode
    still = [n for n in ("Cx", "Cy", "Cz", "V")
             if not os.path.isfile(os.path.join(case, end_dir, n))]
    if still:
        return False, "postProcess wrote no " + " ".join(still)
    return True, "written"


def read_mesh(case, end_dir):
    """Radius, height and volume of every cell, from the written geometry."""
    cx = read_internal(os.path.join(case, end_dir, "Cx"))
    cy = read_internal(os.path.join(case, end_dir, "Cy"))
    cz = read_internal(os.path.join(case, end_dir, "Cz"))
    vv = read_internal(os.path.join(case, end_dir, "V"))
    if not (cx and cy and cz and vv):
        return None
    if not (len(cx) == len(cy) == len(cz) == len(vv)):
        return None
    r = [math.hypot(cx[i], cy[i]) for i in range(len(cx))]
    return dict(r=r, z=cz, V=vv, n=len(cx))


def resolve_planes(mesh, nz, nr_total):
    """Group cells into axial planes and order each plane by radius.

    Returns (planes, reason).  planes is a list of dict(z=..., idx=[...]) with
    idx ordered by increasing radius, or None with a reason on any structural
    disagreement -- which is a REFUSAL condition, "mesh/reader inconsistency"
    in the section 12 S6 contract.
    """
    if mesh["n"] != nz * nr_total:
        return None, ("mesh has %d cells; %d planes x %d radial = %d"
                      % (mesh["n"], nz, nr_total, nz * nr_total))
    dz = H_DOMAIN / float(nz)
    order = sorted(range(mesh["n"]), key=lambda i: mesh["z"][i])
    planes, cur, z0 = [], [], None
    for i in order:
        zi = mesh["z"][i]
        if z0 is None or abs(zi - z0) < 0.25 * dz:
            if z0 is None:
                z0 = zi
            cur.append(i)
        else:
            planes.append(cur)
            cur, z0 = [i], zi
    if cur:
        planes.append(cur)
    if len(planes) != nz:
        return None, "grouped %d axial planes; registered %d" % (len(planes), nz)
    out = []
    for grp in planes:
        if len(grp) != nr_total:
            return None, ("a plane holds %d cells; registered %d"
                          % (len(grp), nr_total))
        grp = sorted(grp, key=lambda i: mesh["r"][i])
        out.append(dict(z=sum(mesh["z"][i] for i in grp) / len(grp), idx=grp))
    # section 12 S3 depends on r2 = 3*r1 EXACTLY (both columns in radial block
    # 1, uniform dr).  If that fails the (9f1 - f2)/8 extrapolation is not the
    # registered instrument and the comparator must not proceed.
    i1, i2 = out[0]["idx"][0], out[0]["idx"][1]
    r1, r2 = mesh["r"][i1], mesh["r"][i2]
    if r1 <= 0.0 or abs(r2 / r1 - 3.0) > 1e-9:
        return None, ("r2/r1 = %.12f, not 3 -- the section 12 S3 centreline "
                      "extrapolation is not applicable" % (r2 / r1))
    return out, "ok"


def check_scale_against_mesh(mesh):
    """Section 12 S3: assert SCALE against the mesh's own total volume.

    The flat-sided wedge of half-angle th over 0 <= r <= R, 0 <= z <= H has
    volume sin(th)cos(th) R^2 H, and the full annulus is pi R^2 H, so
    SCALE * sum(V) == pi R^2 H identically.  Refuses on > 1e-6 relative.
    """
    vtot = sum(mesh["V"])
    if vtot <= 0.0:
        return False, 0.0, 0.0
    scale_from_mesh = math.pi * R_DOMAIN ** 2 * H_DOMAIN / vtot
    rel = abs(scale_from_mesh / SCALE - 1.0)
    return rel <= SCALE_REL_TOL, scale_from_mesh, rel


# ===========================================================================
# section 12 S3 -- how each quantity comes off the mesh
# ===========================================================================
def read_plane_quantities(mesh, planes, T, Uz, nz):
    """Per-plane centreline T and w, and the flux integrals Q, M, F, b.

    Centreline (section 12 S3): quadratic-in-r extrapolation to the axis from
    the two axis-adjacent columns, which with r2 = 3*r1 is exactly
    f_c = (9 f1 - f2)/8.  Symmetry-consistent and not a mesh-dependent
    sampling location.

    Q, M, F: SCALE * sum(q_i V_i) / dz over the CONNECTED region from the axis
    out to the first radius where w changes sign.  b = Q / sqrt(pi M).
    """
    dz = H_DOMAIN / float(nz)
    out = []
    for p in planes:
        idx = p["idx"]
        i1, i2 = idx[0], idx[1]
        Tc = (9.0 * T[i1] - T[i2]) / 8.0
        wc = (9.0 * Uz[i1] - Uz[i2]) / 8.0
        sel = []
        for i in idx:
            if Uz[i] > 0.0:
                sel.append(i)
            else:
                break
        Q = SCALE * sum(Uz[i] * mesh["V"][i] for i in sel) / dz
        M = SCALE * sum(Uz[i] ** 2 * mesh["V"][i] for i in sel) / dz
        F = SCALE * sum(Uz[i] * G_ACCEL * BETA * (T[i] - TREF) * mesh["V"][i]
                        for i in sel) / dz
        b = Q / math.sqrt(math.pi * M) if M > 0.0 else float("nan")
        out.append(dict(z=p["z"], Tc=Tc, wc=wc, Q=Q, M=M, F=F, b=b,
                        n_sel=len(sel), amb_dT=T[idx[-1]] - TREF))
    return out


def interp_at(zs, vals, z):
    """Linear interpolation between the two bracketing axial cell-centre
    planes (section 4).  None outside the range."""
    if z < zs[0] or z > zs[-1]:
        return None
    lo = 0
    hi = len(zs) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if zs[mid] <= z:
            lo = mid
        else:
            hi = mid
    if zs[hi] == zs[lo]:
        return vals[lo]
    f = (z - zs[lo]) / (zs[hi] - zs[lo])
    return vals[lo] + f * (vals[hi] - vals[lo])


def read_stations(pq, stations_zd):
    """Every registered quantity at every registered station."""
    zs = [p["z"] for p in pq]
    keys = ("Tc", "wc", "Q", "M", "F", "b", "amb_dT")
    out = dict(z=[], zD=[])
    for k in keys:
        out[k] = []
    for zd in stations_zd:
        z = zd * D_SOURCE
        vals = {}
        for k in keys:
            vals[k] = interp_at(zs, [p[k] for p in pq], z)
        if any(v is None for v in vals.values()):
            return None, "station z/D = %.1f is outside the mesh" % zd
        out["z"].append(z)
        out["zD"].append(zd)
        for k in keys:
            out[k].append(vals[k])
    out["dT"] = [t - TREF for t in out["Tc"]]
    return out, "ok"


# ===========================================================================
# fits
# ===========================================================================
def ols(xs, ys):
    """Ordinary least squares slope and intercept, plus R^2."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0.0:
        return None, None, None
    s = sxy / sxx
    c = my - s * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (s * x + c)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return s, c, r2


def fit_radius(st):
    """Section 12 S4: b(z) = s (z - z0) by OLS; z0 is the x-intercept and
    alpha = (5/6) s.  b is REPORT-ONLY, so z0 carries no circularity into the
    graded exponents -- it is not derived from w, dT or Q."""
    s, c, r2 = ols(st["z"], st["b"])
    if s is None or s == 0.0:
        return None
    z0 = -c / s
    return dict(slope=s, z0=z0, r2=r2, alpha=(5.0 / 6.0) * s)


def fit_exponents(st, z0):
    """Section 3: OLS of ln(quantity) on ln(z - z0)."""
    out = dict(n_w=None, n_T=None, n_Q=None,
               r2_w=None, r2_T=None, r2_Q=None, why="")
    xs, yw, yt, yq = [], [], [], []
    for i in range(len(st["z"])):
        zz = st["z"][i] - z0
        if zz <= 0.0 or st["wc"][i] <= 0.0 or st["dT"][i] <= 0.0 \
                or st["Q"][i] <= 0.0:
            out["why"] = ("non-positive quantity or z - z0 <= 0 at z/D = %.1f "
                          "-- a log-log fit is not defined" % st["zD"][i])
            return out
        xs.append(math.log(zz))
        yw.append(math.log(st["wc"][i]))
        yt.append(math.log(st["dT"][i]))
        yq.append(math.log(st["Q"][i]))
    out["n_w"], _, out["r2_w"] = ols(xs, yw)
    out["n_T"], _, out["r2_T"] = ols(xs, yt)
    out["n_Q"], _, out["r2_Q"] = ols(xs, yq)
    return out


# ===========================================================================
# CLAUDE.md rule 5 -- the Roache triple, this file's OWN routine
# ===========================================================================
def gci_triple(f_coarse, f_med, f_fine, r=R_REFINE, fs=FS):
    """Equal-ratio Roache triple.  States and thresholds match the lab's
    canon (analyse_t3.gci_unequal at r21 == r32, ported in
    scripts/roache_triple.py); the Richardson SIGN is the corrected one.

        e21 = f_med - f_fine,   e32 = f_coarse - f_med
        p   = ln|e32/e21| / ln r
        GCI = Fs |e21/f_fine| / (r^p - 1)
        richardson = f_fine - e21/den          <-- CORRECT (section 12 S5)

    richardson_parent_convention is the "+" form the two parent comparators
    return, given that explicit name so a reader comparing against a published
    thermal number can see both and know which is which.  NOTHING in this file
    is gated on either (ruling R1).
    """
    e21 = f_med - f_fine
    e32 = f_coarse - f_med
    base = dict(state=None, order=None, e21=e21, e32=e32, ratio=None,
                GCI_pct=None, GCI_abs=None, richardson=None,
                richardson_parent_convention=None, r=r, dim=DIM, fs=fs)
    if e21 == 0.0:
        base["state"] = "EXACT"
        return base
    ratio = e32 / e21
    base["ratio"] = ratio
    if ratio < 0.0:
        base["state"] = "OSCILLATORY"
        return base
    p = math.log(abs(ratio)) / math.log(r)
    base["order"] = p
    if p <= 0.0:
        base["state"] = "DIVERGENT"
        return base
    if p < 0.5:
        base["state"] = "STAGNANT"
        return base
    den = r ** p - 1.0
    base["state"] = "CONVERGING"
    base["GCI_pct"] = 100.0 * fs * abs(e21 / f_fine) / den if f_fine != 0 else None
    base["GCI_abs"] = fs * abs(e21) / den
    base["richardson"] = f_fine - e21 / den
    base["richardson_parent_convention"] = f_fine + e21 / den
    return base


def band_verdict(row, value):
    """Section 7 criterion (3), computed FIRST and UNCONDITIONALLY.

    The gate is one-way (CLAUDE.md rule 5): it may turn this PASS or GATE FAIL
    INTO a NOT A RESULT and may never do the reverse.  That is enforced
    structurally in grade_row by an assertion, not by care.
    """
    ex = EXACT[row]
    dev = value - ex
    util = abs(dev) / BAND_HALF_WIDTH
    inside = abs(dev) <= BAND_HALF_WIDTH
    return (VERDICT_PASS if inside else VERDICT_FAIL), dev, util


# ===========================================================================
# section 9 -- the planted zero (CLAUDE.md rule 3)
# ===========================================================================
def plant_into_T(src_case, end_dir, tmp_dir, targets, amount):
    """Write a copy of the endTime T with `amount` added in `targets` cells.

    The copy is a temporary case: the endTime directory alone, holding the
    written cell geometry and the perturbed field.  The reader is then pointed
    at the copy and must report the perturbation THROUGH THE SAME CODE PATH a
    real read uses.
    """
    dst = os.path.join(tmp_dir, end_dir)
    os.makedirs(dst, exist_ok=True)
    for n in ("Cx", "Cy", "Cz", "V", "U"):
        shutil.copy2(os.path.join(src_case, end_dir, n), os.path.join(dst, n))
    vals = read_internal(os.path.join(src_case, end_dir, "T"))
    if vals is None:
        return None
    out = list(vals)
    for i in targets:
        out[i] = out[i] + amount
    if not write_internal(os.path.join(src_case, end_dir, "T"),
                          os.path.join(dst, "T"), out, vector=False):
        return None
    return tmp_dir


def plant_into_Uz(src_case, end_dir, tmp_dir, targets, amount):
    """The same plant applied to U_z, checked against the w_c(z) reader."""
    dst = os.path.join(tmp_dir, end_dir)
    os.makedirs(dst, exist_ok=True)
    for n in ("Cx", "Cy", "Cz", "V", "T"):
        shutil.copy2(os.path.join(src_case, end_dir, n), os.path.join(dst, n))
    vals = read_internal(os.path.join(src_case, end_dir, "U"), vector=True)
    if vals is None:
        return None
    out = [list(v) for v in vals]
    for i in targets:
        out[i][2] = out[i][2] + amount
    if not write_internal(os.path.join(src_case, end_dir, "U"),
                          os.path.join(dst, "U"),
                          [tuple(v) for v in out], vector=True):
        return None
    return tmp_dir


def _read_centrelines(case_like, end_dir, nz, nr_total):
    """Run the FULL station reader over a directory holding an endTime dir."""
    mesh = read_mesh(case_like, end_dir)
    if mesh is None:
        return None, "cannot read geometry"
    planes, why = resolve_planes(mesh, nz, nr_total)
    if planes is None:
        return None, why
    T = read_internal(os.path.join(case_like, end_dir, "T"))
    U = read_internal(os.path.join(case_like, end_dir, "U"), vector=True)
    if T is None or U is None:
        return None, "cannot read T or U"
    Uz = [u[2] for u in U]
    pq = read_plane_quantities(mesh, planes, T, Uz, nz)
    st, why = read_stations(pq, STATIONS_ZD)
    if st is None:
        return None, why
    return st, "ok"


def check_planted_zero(case, end_dir, nz, nr_total):
    """Section 9, in full, plus two supplementary reader-integrity controls.

    REGISTERED ARM (section 9).  PLANT = 1.234e-03 added to every cell of the
    TWO axis-adjacent radial columns at every axial level, in a copy on disk.
    Because the section 12 S3 extrapolation is (9 f1 - f2)/8, shifting BOTH
    columns by PLANT shifts the extrapolated centreline by (9P - P)/8 = P
    EXACTLY.  The expected response is analytic, not approximate.  Required at
    every one of the 31 registered stations, tolerance 1e-9.  Same plant, same
    terms, same refusal, for U_z against the w_c(z) reader.

    SUPPLEMENTARY ARMS, added by this file and labelled as such.  They invent
    no threshold: both expected responses are exact arithmetic identities, so
    neither can fire on a physically awkward case, only on a broken reader.
      (a) plant into the INNERMOST column only -> centreline must shift by
          exactly 9P/8.  A reader that had silently selected the wrong pair of
          columns would agree with the registered arm and disagree here.
      (b) plant into the two OUTERMOST columns -> centreline must not move.
          This zero is admissible ONLY because arms (a) and the registered arm
          have already shown this same reader seeing a non-zero.
    """
    base, why = _read_centrelines(case, end_dir, nz, nr_total)
    if base is None:
        return False, "planted-zero control: baseline read failed -- " + why, []

    mesh = read_mesh(case, end_dir)
    planes, why = resolve_planes(mesh, nz, nr_total)
    if planes is None:
        return False, "planted-zero control: " + why, []
    inner2 = sorted({i for p in planes for i in p["idx"][:2]})
    inner1 = sorted({p["idx"][0] for p in planes})
    outer2 = sorted({i for p in planes for i in p["idx"][-2:]})

    arms = [("T   registered  both axis-adjacent columns", plant_into_T,
             inner2, PLANT, "dT", PLANT),
            ("U_z registered  both axis-adjacent columns", plant_into_Uz,
             inner2, PLANT, "wc", PLANT),
            ("T   supplementary (a) innermost column only", plant_into_T,
             inner1, PLANT, "dT", 9.0 * PLANT / 8.0),
            ("U_z supplementary (a) innermost column only", plant_into_Uz,
             inner1, PLANT, "wc", 9.0 * PLANT / 8.0),
            ("T   supplementary (b) two OUTERMOST columns", plant_into_T,
             outer2, PLANT, "dT", 0.0),
            ("U_z supplementary (b) two OUTERMOST columns", plant_into_Uz,
             outer2, PLANT, "wc", 0.0)]

    lines, ok_all = [], True
    for name, fn, targets, amount, key, expect in arms:
        tmp = tempfile.mkdtemp(prefix="t8_plant_")
        try:
            if fn(case, end_dir, tmp, targets, amount) is None:
                lines.append(("FAIL", name, "could not write the planted copy"))
                ok_all = False
                continue
            got, why = _read_centrelines(tmp, end_dir, nz, nr_total)
            if got is None:
                lines.append(("FAIL", name, "read-back failed -- " + why))
                ok_all = False
                continue
            worst = max(abs((got[key][i] - base[key][i]) - expect)
                        for i in range(len(STATIONS_ZD)))
            good = worst <= PLANT_TOL
            lines.append(("PASS" if good else "FAIL", name,
                          "expected shift %.9e at all %d stations; worst "
                          "deviation %.3e (tol %.0e)"
                          % (expect, len(STATIONS_ZD), worst, PLANT_TOL)))
            ok_all = ok_all and good
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return ok_all, ("seen at every station" if ok_all
                    else "THE READER COULD NOT SEE THE PLANT"), lines


# ===========================================================================
# grading
# ===========================================================================
def new_row(row):
    """THE ONLY constructor for a graded-row record (probe A, structurally)."""
    return dict(row=row, exact=EXACT[row], value=None, dev=None, util=None,
                band=None, verdict=None, why="", triple=None,
                coarse=None, med=None, fine=None,
                conv={}, plateau_note="", gci=None)


def grade_row(row, vals, conv_by_level, plateau_by_level):
    """CLAUDE.md rule 5 and section 7, IN THE FIXED ORDER AND ONLY THIS ORDER.

    (1) any level not iteratively converged OR not plateaued -> NOT A RESULT.
        THIS FIRES BEFORE THE TRIPLE IS CLASSIFIED, per level, against that
        level's own criterion.  ansys-verification returned NOT A RESULT on a
        VMFL051 row sitting a comfortable -0.2337 % inside a +/-0.5 % band
        because two of three levels never plateaued: the comfort of the
        deviation is not evidence about the levels.
    (2) triple not CONVERGING -> NOT A RESULT, with the value, BOTH triples
        and the order printed beside it.
    (3) CONVERGING -> PASS inside the band else GATE FAIL, GCI at Fs = 1.25
        printed either way, deviation and band utilisation printed either way.
    """
    rec = new_row(row)
    rec["coarse"], rec["med"], rec["fine"] = vals["c"], vals["m"], vals["f"]
    rec["value"] = vals["f"]                      # R1: the FINE value is graded
    rec["conv"] = dict(conv_by_level)
    rec["plateau_note"] = plateau_by_level

    # -- the band verdict is computed FIRST and UNCONDITIONALLY --------------
    band, dev, util = band_verdict(row, rec["value"])
    rec["band"], rec["dev"], rec["util"] = band, dev, util

    # -- (1) BEFORE the triple is classified --------------------------------
    bad = [lv for lv in LEVELS
           if conv_by_level.get(lv, {}).get("state") != "CONVERGED"]
    if bad:
        rec["verdict"] = VERDICT_NAR
        rec["why"] = ("criterion (1): level(s) " + ",".join(bad) +
                      " not iteratively converged on field " +
                      SOURCE_FIELD[row])
    else:
        tr = gci_triple(vals["c"], vals["m"], vals["f"])
        rec["triple"] = tr
        if tr["state"] != "CONVERGING":
            rec["verdict"] = VERDICT_NAR
            rec["why"] = "criterion (2): triple is " + tr["state"]
        else:
            rec["verdict"] = band
            rec["gci"] = tr["GCI_pct"]
            rec["why"] = ("criterion (3): fine value %s the band"
                          % ("inside" if band == VERDICT_PASS else "outside"))

    # -- THE GATE IS ONE-WAY.  Structural, not careful. ---------------------
    assert rec["verdict"] in (band, VERDICT_NAR), (
        "the gate turned a %s into a %s -- forbidden by CLAUDE.md rule 5"
        % (band, rec["verdict"]))
    return rec


# ===========================================================================
# reporting
# ===========================================================================
def hr(title):
    print("")
    print("=" * 78)
    print(title)
    print("=" * 78)


def print_row(rec):
    print("")
    print("  %-4s  exact %+.6f   FINE (graded, R1) %s"
          % (rec["row"], rec["exact"],
             "None" if rec["value"] is None else "%+.6f" % rec["value"]))
    print("        coarse %s   medium %s   fine %s"
          % tuple("None" if rec[k] is None else "%+.6f" % rec[k]
                  for k in ("coarse", "med", "fine")))
    if rec["dev"] is not None:
        print("        deviation %+.6f   band utilisation %.4f of +/-%.2f "
              "(R2b)" % (rec["dev"], rec["util"], BAND_HALF_WIDTH))
    tr = rec["triple"]
    if tr is not None:
        print("        triple %s   e21 %+.6e   e32 %+.6e   ratio %s"
              % (tr["state"], tr["e21"], tr["e32"],
                 "None" if tr["ratio"] is None else "%+.6f" % tr["ratio"]))
        print("        observed order %s   at r = %.1f, dim = %d"
              % ("None" if tr["order"] is None else "%.4f" % tr["order"],
                 tr["r"], tr["dim"]))
        if tr["state"] == "CONVERGING":
            print("        GCI %.4f %% at Fs = %.2f   (GCI_abs %.6e)"
                  % (tr["GCI_pct"], tr["fs"], tr["GCI_abs"]))
            print("        Richardson extrapolate %+.6f  REPORTED ONLY -- no "
                  "verdict is a function of it (R1)" % tr["richardson"])
            print("        [parent-convention form %+.6f, shown so a reader "
                  "comparing a published thermal number knows which is which]"
                  % tr["richardson_parent_convention"])
        else:
            print("        NO GCI IS QUOTED: the three values are not "
                  "monotone (CLAUDE.md rule 5)")
    print("        band verdict computed first and unconditionally: %s"
          % rec["band"])
    print("        VERDICT: %s   -- %s" % (rec["verdict"], rec["why"]))


# ===========================================================================
# the run
# ===========================================================================
def grade(root):
    hr("T8 -- MTT pure-plume self-similarity.  THE GRADING PATH.")
    print("pre-registration: docs/campaigns/T-family/T8_PREREGISTRATION.md")
    print("CLAUDE.md rules 1-5 and 12 bind this file; the verdict vocabulary "
          "is PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / "
          "PENDING and nothing else.")

    hr("section 11 -- freeze set hashed against the committed blob")
    ok, lines = check_freeze_set()
    for ln in lines:
        print(ln)
    if not ok:
        refuse("the section 11 freeze set does not match HEAD.  An "
               "uncommitted pre-registration is NOT FROZEN, and grading "
               "against an unfrozen document is exactly the defect this rung "
               "was written to avoid.  Commit the freeze set, then grade.")

    hr("section 12 S3 -- the wedge scale")
    print("  SCALE = 2*pi/sin(%.1f deg) = %.10f   [FORMULA GOVERNS]"
          % (WEDGE_FULL_DEG, SCALE))
    print("  identity check pi/(sin th cos th) = %.10f"
          % (math.pi / (math.sin(WEDGE_HALF_RAD) * math.cos(WEDGE_HALF_RAD))))
    print("  NOTE: the document prints '= 72.0928'; the formula gives "
          "%.5f.  The printed decimal is a rounding error of %.2e relative, "
          "LARGER than the 1e-6 assertion tolerance registered in the same "
          "sentence.  This file uses the formula." % (SCALE, abs(72.0928 / SCALE - 1.0)))

    # ---------------- per level -------------------------------------------
    levels = {}
    for lv in LEVELS:
        rec = new_level(lv)
        rec["case"] = os.path.join(root, "T8_MTT_" + lv)
        levels[lv] = rec

    hr("CLAUDE.md rule 4 -- strict completion, every clause, every level")
    for lv in LEVELS:
        rec = levels[lv]
        good, reason, cl = check_completion(rec["case"], lv, root)
        rec["complete"], rec["reason"], rec["clauses"] = good, reason, cl
        print("")
        print("  level %s   %s" % (lv, rec["case"]))
        for state, name, detail in cl:
            print("    [%s] %-46s %s" % (state, name, detail))
        print("    -> %s" % ("COMPLETE" if good else "NOT COMPLETE: " + reason))
    bad = [lv for lv in LEVELS if not levels[lv]["complete"]]
    if bad:
        refuse("strict completion (CLAUDE.md rule 4) unmet on level(s) " +
               ",".join(bad) + ".  A run that fails any clause is not done.")

    # ---------------- mesh, geometry, readers ------------------------------
    hr("the mesh, read from the mesh")
    for lv in LEVELS:
        rec = levels[lv]
        cd = open(os.path.join(rec["case"], "system", "controlDict")).read()
        rec["end_time"] = float(re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;",
                                          cd, re.M).group(1))
        rec["end_dir"] = resolve_end_time_dir(rec["case"], rec["end_time"])
        good, why = ensure_cell_geometry(rec["case"], rec["end_dir"])
        if not good:
            refuse("level %s: cell geometry could not be written -- %s" % (lv, why))
        mesh = read_mesh(rec["case"], rec["end_dir"])
        if mesh is None:
            refuse("level %s: cannot read the written cell geometry" % lv)
        nz = int(read_case_txt(rec["case"], "nz"))
        nr_total = sum(int(x) for x in
                       read_case_txt(rec["case"], "nr_blocks").split("/"))
        n_expect = int(read_case_txt(rec["case"], "n_cells_expected"))
        if mesh["n"] != n_expect:
            refuse("level %s: mesh has %d cells, registered %d "
                   "(mesh/reader inconsistency)" % (lv, mesh["n"], n_expect))
        planes, why = resolve_planes(mesh, nz, nr_total)
        if planes is None:
            refuse("level %s: %s (mesh/reader inconsistency)" % (lv, why))
        good, sfm, srel = check_scale_against_mesh(mesh)
        if not good:
            refuse("level %s: SCALE assertion failed -- mesh gives %.10f "
                   "against registered %.10f, %.3e relative (> %.0e)"
                   % (lv, sfm, SCALE, srel, SCALE_REL_TOL))
        rec["mesh"], rec["planes"], rec["n_cells"] = mesh, planes, mesh["n"]
        rec["nz"], rec["nr_total"] = nz, nr_total
        print("  level %s  cells %6d  planes %4d  radial %4d  SCALE from mesh "
              "%.10f  (%.2e relative)" % (lv, mesh["n"], nz, nr_total, sfm, srel))

    # r is registered, never inferred -- but the consistency check is printed
    ratio_cm = levels["m"]["n_cells"] / float(levels["c"]["n_cells"])
    ratio_mf = levels["f"]["n_cells"] / float(levels["m"]["n_cells"])
    print("")
    print("  refinement ratio r = %.1f, REGISTERED by section 5 (every block's "
          "divisions doubled in both directions)." % R_REFINE)
    print("  dim = %d, and the cell-count ratios %.4f / %.4f are a CONSISTENCY "
          "CHECK against r**dim = %.4f -- never the source of r "
          "(VERIFICATION_CHARTER 3.1)."
          % (DIM, ratio_cm, ratio_mf, R_REFINE ** DIM))
    if abs(ratio_cm - R_REFINE ** DIM) > 1e-9 or \
            abs(ratio_mf - R_REFINE ** DIM) > 1e-9:
        refuse("the cell-count ratios do not match r**dim; the ladder on disk "
               "is not the registered ladder (mesh/reader inconsistency)")

    # ---------------- section 9 -- the planted zero ------------------------
    hr("section 9 -- the planted zero (CLAUDE.md rule 3), on the FINE level")
    f = levels["f"]
    ok, reason, plines = check_planted_zero(f["case"], f["end_dir"],
                                            f["nz"], f["nr_total"])
    for state, name, detail in plines:
        print("  [%s] %-48s %s" % (state, name, detail))
    if not ok:
        refuse("the planted zero was NOT SEEN: " + reason + ".  A zero from a "
               "reader not shown able to see a non-zero is not evidence.")
    print("  -> the reader is armed.")

    # ---------------- readers ---------------------------------------------
    hr("section 12 S3 -- station values")
    st_by_level, c5_by_level = {}, {}
    for lv in LEVELS:
        rec = levels[lv]
        T = read_internal(os.path.join(rec["case"], rec["end_dir"], "T"))
        U = read_internal(os.path.join(rec["case"], rec["end_dir"], "U"),
                          vector=True)
        if T is None or U is None:
            refuse("level %s: cannot read T or U at endTime" % lv)
        Uz = [u[2] for u in U]
        pq = read_plane_quantities(rec["mesh"], rec["planes"], T, Uz, rec["nz"])
        st, why = read_stations(pq, STATIONS_ZD)
        if st is None:
            refuse("level %s: %s" % (lv, why))
        c5, why = read_stations(pq, C5_STATIONS_ZD)
        if c5 is None:
            refuse("level %s (C5 window): %s" % (lv, why))
        st_by_level[lv], c5_by_level[lv] = st, c5
        print("  level %s  %d graded stations z/D %.1f..%.1f, %d C5 stations"
              % (lv, len(STATIONS_ZD), STATIONS_ZD[0], STATIONS_ZD[-1],
                 len(C5_STATIONS_ZD)))

    # ---------------- section 9 C1 -- the one control that can gate --------
    hr("section 9 C1 -- far-field quiescence (THE ONE CONTROL THAT CAN GATE)")
    c1_ok = True
    for lv in LEVELS:
        st = st_by_level[lv]
        worst, worst_zd = 0.0, None
        for i in range(len(STATIONS_ZD)):
            if st["dT"][i] <= 0.0:
                c1_ok = False
                continue
            frac = abs(st["amb_dT"][i]) / st["dT"][i]
            if frac > worst:
                worst, worst_zd = frac, st["zD"][i]
        good = worst < C1_AMBIENT_FRACTION
        c1_ok = c1_ok and good
        print("  level %s  worst ambient dT / centreline dT = %.5f at z/D = %s "
              "  (< %.2f required)  %s"
              % (lv, worst, worst_zd, C1_AMBIENT_FRACTION,
                 "PASS" if good else "FAIL"))
    if not c1_ok:
        print("  -> C1 FAILED: the domain is too narrow for the reference's "
              "own precondition.  EVERY graded row is NOT A RESULT.")

    # ---------------- fits -------------------------------------------------
    hr("sections 3, 4 and 12 S4 -- the fits")
    fits, radii, c5fits = {}, {}, {}
    for lv in LEVELS:
        rad = fit_radius(st_by_level[lv])
        if rad is None:
            refuse("level %s: the b(z) radius fit is degenerate; section 12 S4 "
                   "z0 is undefined" % lv)
        radii[lv] = rad
        fits[lv] = fit_exponents(st_by_level[lv], rad["z0"])
        c5fits[lv] = fit_exponents(c5_by_level[lv], rad["z0"])
        print("  level %s  z0 = %+.6f m   b-fit slope %.6f  R2 %.6f   "
              "alpha = (5/6)s = %.6f  [REPORT ONLY]"
              % (lv, rad["z0"], rad["slope"], rad["r2"], rad["alpha"]))
        if fits[lv]["why"]:
            refuse("level %s: %s" % (lv, fits[lv]["why"]))
        print("           n_w %+.6f (R2 %.6f)   n_T %+.6f (R2 %.6f)   "
              "n_Q %+.6f (R2 %.6f)"
              % (fits[lv]["n_w"], fits[lv]["r2_w"], fits[lv]["n_T"],
                 fits[lv]["r2_T"], fits[lv]["n_Q"], fits[lv]["r2_Q"]))

    # ---------------- criterion (1), per level, BEFORE the triple ----------
    hr("section 7 criterion (1) -- iterative convergence, LEVEL BY LEVEL")
    print("  norm: max|a-b| / (max(b)-min(b)) over the internal field between "
          "the last two WRITTEN checkpoints, tol %.0e (section 7).  This is "
          "the lab's standing meaning of that phrase "
          "(analyse_t1c.iterative_convergence:197), REIMPLEMENTED here, not "
          "imported (section 12 S5)." % CONV_REL_TOL)
    conv = {}
    for lv in LEVELS:
        conv[lv] = {}
        for fld in ("T", "U"):
            c = check_iterative_convergence(levels[lv]["case"], fld)
            conv[lv][fld] = c
            print("  level %s  field %-5s  %-14s rel = %s  between %s"
                  % (lv, fld, c["state"],
                     "n/a" if c["rel"] is None else "%.3e" % c["rel"],
                     c["between"]))
    plateau_note = (
        "the section 7 conjunct 'and plateaued' has NO separately registered "
        "criterion in T8 (PLATEAU_MAX_EXPONENT_DRIFT is None); clause (1) is "
        "implemented as the em-dash definition alone, and this is stated "
        "rather than chosen quietly")
    if PLATEAU_MAX_EXPONENT_DRIFT is None:
        print("")
        print("  PLATEAU CONJUNCT: " + plateau_note + ".")
        print("  SUPERVISOR RULING REQUIRED BEFORE THIS RUNG IS FIRED.")
    else:
        print("")
        print("  PLATEAU CONJUNCT: separate criterion registered, max "
              "exponent drift %.3e between the last two checkpoints."
              % PLATEAU_MAX_EXPONENT_DRIFT)

    # ---------------- grade -----------------------------------------------
    hr("CLAUDE.md rule 5 / section 7 -- the graded rows")
    rows = []
    for row in ROWS:
        vals = {lv: fits[lv][row] for lv in LEVELS}
        cbl = {lv: conv[lv][SOURCE_FIELD[row]] for lv in LEVELS}
        rec = grade_row(row, vals, cbl, plateau_note)
        if not c1_ok and rec["verdict"] != VERDICT_NAR:
            rec["verdict"] = VERDICT_NAR
            rec["why"] = ("control C1 failed: ambient dT is not < 1 %% of the "
                          "centreline; the reference's own precondition does "
                          "not hold")
            assert rec["verdict"] in (rec["band"], VERDICT_NAR)
        rows.append(rec)
        print_row(rec)

    # ---------------- the report-only controls -----------------------------
    hr("section 9 -- the registered controls, reported whichever way they fall")
    for lv in LEVELS:
        st = st_by_level[lv]
        Fs_ = st["F"]
        mean = sum(Fs_) / len(Fs_)
        spread = (max(Fs_) - min(Fs_)) / abs(mean) if mean != 0 else float("nan")
        print("  C2 level %s  buoyancy flux F: mean %.6e, spread %.4f %% "
              "across the window (%.0f %% tolerance)  %s"
              % (lv, mean, 100.0 * spread, 100.0 * C2_FLUX_TOL,
                 "conserved" if spread < C2_FLUX_TOL else
                 "NOT CONSERVED -- this invalidates THE REFERENCE, not the "
                 "solver"))
    z0s = [radii[lv]["z0"] for lv in LEVELS]
    print("  C3 virtual origin z0: c %+.6f  m %+.6f  f %+.6f   spread %.6f m"
          % (z0s[0], z0s[1], z0s[2], max(z0s) - min(z0s)))
    for lv in LEVELS:
        z0f = fit_exponents(st_by_level[lv], 0.0)
        if z0f["why"]:
            print("     level %s at z0 = 0: %s" % (lv, z0f["why"]))
        else:
            print("     level %s at z0 = 0:  n_w %+.6f  n_T %+.6f  n_Q %+.6f"
                  % (lv, z0f["n_w"], z0f["n_T"], z0f["n_Q"]))
    nw = fits["f"]["n_w"]
    d_jet = abs(nw - (-1.0)) / (2.0 * BAND_HALF_WIDTH)
    d_plume = abs(nw - EXACT["n_w"]) / (2.0 * BAND_HALF_WIDTH)
    print("  C4 jet discriminator: fine n_w = %+.6f is %.3f band widths from "
          "the jet value -1 and %.3f from the plume value -1/3  -> %s"
          % (nw, d_jet, d_plume,
             "the fit can tell a plume from a jet" if d_jet > d_plume
             else "THE FIT CANNOT TELL A PLUME FROM A JET"))
    print("  C5 fit-window sensitivity (z/D in [10,30], 41 stations, "
          "REPORTED, NEVER GATED):")
    for row in ROWS:
        a, b = fits["f"][row], c5fits["f"][row]
        if b is None:
            continue
        d = abs(a - b)
        print("     %-4s graded window %+.6f   C5 window %+.6f   |diff| %.6f%s"
              % (row, a, b, d,
                 "   DISCLOSED: MORE THAN ONE BAND WIDTH (%.2f)"
                 % C5_DISCLOSE_DELTA if d > C5_DISCLOSE_DELTA else ""))

    hr("section 9 -- registered prediction P1 (ruling R4)")
    alpha_f = radii["f"]["alpha"]
    in_pub = ALPHA_PUBLISHED[0] <= alpha_f <= ALPHA_PUBLISHED[1]
    in_band = all(r["band"] == VERDICT_PASS for r in rows)
    print("  alpha (fine, REPORT-ONLY, no gate) = %.6f; published pure-plume "
          "range %.2f-%.2f -> %s"
          % (alpha_f, ALPHA_PUBLISHED[0], ALPHA_PUBLISHED[1],
             "inside" if in_pub else "OUTSIDE"))
    if not in_band:
        print("  P1 WRONG -- the graded exponents moved.  P1 predicted the "
              "kEpsilon round-jet/plane-jet anomaly would bias alpha and NOT "
              "move n_w, n_T, n_Q.  It did.  Reported as wrong, in those "
              "words, as section 9 requires.")
    elif not in_pub:
        print("  P1 CONFIRMED -- alpha is outside the published range while "
              "all three exponents are in band, which is exactly what P1 "
              "predicted before the run.")
    else:
        print("  P1 neither confirmed nor refuted: alpha is inside the "
              "published range, so the anomaly did not bias it measurably "
              "here.  P1 armed no gate either way.")

    # ---------------- cost, CLAUDE.md rule 12 ------------------------------
    hr("CLAUDE.md rule 12 -- estimate versus actual (inputs for "
       "docs/COST_CALIBRATION.md)")
    tot_a, tot_p = 0.0, 0.0
    for lv in LEVELS:
        st = read_status(root, lv)
        act = float(st["core_min"])
        pred = PREDICTED_CORE_MIN[lv]
        tot_a += act
        tot_p += pred
        print("  level %s  predicted %8.2f core-min   actual %8.2f core-min   "
              "ratio %.3f   cap %d   wall %s s   ranks %s"
              % (lv, pred, act, act / pred, CAP_CORE_MIN[lv],
                 st.get("wall_s"), st.get("ranks")))
    print("  WHOLE RUNG  predicted %.2f   actual %.2f   ratio %.3f"
          % (tot_p, tot_a, tot_a / tot_p))
    print("  $ derived at $0.0513/core-h (owner-stated; the box cannot read "
          "its own billing): predicted $%.3f, actual $%.3f -- DERIVED, NOT "
          "MEASURED." % (tot_p / 60.0 * 0.0513, tot_a / 60.0 * 0.0513))
    print("  gap attribution: section 8 registered the exposure BEFORE the run "
          "-- the 1.196e5 cell*steps/(core*s) rate is borrowed from K2bU3_L025, "
          "a TRANSIENT PIMPLE case, while T8 is STEADY SIMPLE-family.  Any gap "
          "is MISPREDICTION unless contention or waste is separately named.")

    # ---------------- section 10 and the exit contract ---------------------
    hr("section 10 -- what this rung does not claim")
    print("  This rung can reach GATE REACHED at best and can NEVER reach "
          "HOLDS: MTT is an ANALYTIC reference and scores V, never P.  A PASS "
          "here is a JOINT code-plus-closure statement and is NOT a "
          "code-verification claim (R2a) -- a +/-0.05 modelling-tolerance band "
          "grades discretisation, closure and boundary treatment TOGETHER and "
          "cannot separate them.  The GCI is the only numerical-error "
          "statement made here, and it is reported, not gated.")

    hr("section 12 S6 -- exit contract")
    n_fail = sum(1 for r in rows if r["verdict"] == VERDICT_FAIL)
    n_pass = sum(1 for r in rows if r["verdict"] == VERDICT_PASS)
    for r in rows:
        print("  %-4s  %s" % (r["row"], r["verdict"]))
    if n_fail:
        print("  -> exit 1: %d registered row(s) are GATE FAIL" % n_fail)
        return 1
    if n_pass < len(ROWS):
        print("  -> exit 3: no GATE FAIL, but only %d of %d registered rows "
              "reached the band" % (n_pass, len(ROWS)))
        return 3
    print("  -> exit 0: all %d registered rows reached the band and all are "
          "PASS" % len(ROWS))
    return 0


# ===========================================================================
# --selftest
# ===========================================================================
# ===========================================================================
# selftest fixtures -- a REAL endTime directory on disk
# ===========================================================================
# 2026-08-25 pre-compute amendment A1.  Added so that the section 9 planted
# zero and the section 12 S3 centreline reader are EXERCISED rather than
# described.  Before this, --selftest never called read_mesh, resolve_planes,
# read_plane_quantities, read_stations or check_planted_zero at all: the
# extrapolation weights at read_plane_quantities could be changed from
# (9 f1 - f2)/8 to any other formula and every selftest check still passed.
# A control never shown able to fire is exactly what CLAUDE.md rule 3 refuses
# to accept as evidence, and that refusal applies to this file's own controls.
SYN_NZ = 32                      # planes; dz = H_DOMAIN/32 = 0.25 m
SYN_NR = 8                       # radial cells; dr = R_DOMAIN/8 = 0.3 m


def _foam_header(cls, obj):
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n    object      %s;\n}\n\n"
            "dimensions      [0 0 0 0 0 0 0];\n\n" % (cls, obj))


def write_foam_scalar(path, values):
    """A real OpenFOAM volScalarField, written at full double precision."""
    with open(path, "w") as fh:
        fh.write(_foam_header("volScalarField", os.path.basename(path)))
        fh.write("internalField   nonuniform List<scalar>\n%d\n(\n"
                 % len(values))
        fh.write("\n".join("%.17g" % v for v in values))
        fh.write("\n)\n;\n\nboundaryField\n{\n}\n")


def write_foam_vector(path, values):
    """A real OpenFOAM volVectorField, written at full double precision."""
    with open(path, "w") as fh:
        fh.write(_foam_header("volVectorField", os.path.basename(path)))
        fh.write("internalField   nonuniform List<vector>\n%d\n(\n"
                 % len(values))
        fh.write("\n".join("(%.17g %.17g %.17g)" % tuple(v) for v in values))
        fh.write("\n)\n;\n\nboundaryField\n{\n}\n")


def make_synthetic_field_case(root, end_dir="100", nz=SYN_NZ, nr=SYN_NR,
                              t_curv=-40.0, w_curv=-20.0):
    """Cx, Cy, Cz, V, T and U on disk, T and U_z EXACTLY quadratic in r.

    Exactly quadratic is the whole point.  With cell centres at
    r_j = (j + 1/2) dr the two axis-adjacent columns sit at r1 = dr/2 and
    r2 = 3 dr/2, so r2 = 3 r1 EXACTLY -- the condition resolve_planes
    enforces -- and the registered extrapolation (9 f1 - f2)/8 then returns
    the axis value ANALYTICALLY.  Every assertion built on this fixture is an
    exact identity; none of them is a tolerance chosen to make it pass.

    Returns (root, meta) where meta carries the per-plane analytic axis values
    the shipped reader must reproduce.
    """
    d = os.path.join(root, end_dir)
    os.makedirs(d, exist_ok=True)
    dz = H_DOMAIN / float(nz)
    dr = R_DOMAIN / float(nr)
    cx, cy, cz, vv, tt, uu = [], [], [], [], [], []
    axis_T, axis_w, zs = [], [], []
    for k in range(nz):
        z = (k + 0.5) * dz
        a_T = TREF + 8.0 * (z + 1.0) ** (-5.0 / 3.0)
        a_w = 2.5 * (z + 1.0) ** (-1.0 / 3.0)
        zs.append(z)
        axis_T.append(a_T)
        axis_w.append(a_w)
        for j in range(nr):
            r = (j + 0.5) * dr
            cx.append(r)
            cy.append(0.0)
            cz.append(z)
            vv.append(dz * dr * r)
            tt.append(a_T + t_curv * r * r)
            uu.append((0.0, 0.0, a_w + w_curv * r * r))
    write_foam_scalar(os.path.join(d, "Cx"), cx)
    write_foam_scalar(os.path.join(d, "Cy"), cy)
    write_foam_scalar(os.path.join(d, "Cz"), cz)
    write_foam_scalar(os.path.join(d, "V"), vv)
    write_foam_scalar(os.path.join(d, "T"), tt)
    write_foam_vector(os.path.join(d, "U"), uu)
    return root, dict(nz=nz, nr=nr, dz=dz, dr=dr, z=zs,
                      axis_T=axis_T, axis_w=axis_w)


def mis_weighted_reader(w1, w2, den, tag):
    """A read_plane_quantities REPLACEMENT with the wrong centreline weights.

    Used ONLY by --selftest, and ONLY to prove that the section 9 control can
    SEE a broken extrapolation.  It defers to the real reader for every other
    quantity so that the ONE thing changed is the thing under test.
    """
    real = read_plane_quantities

    def patched(mesh, planes, T, Uz, nz):
        out = real(mesh, planes, T, Uz, nz)
        for p, o in zip(planes, out):
            i1, i2 = p["idx"][0], p["idx"][1]
            o["Tc"] = (w1 * T[i1] - w2 * T[i2]) / den
            o["wc"] = (w1 * Uz[i1] - w2 * Uz[i2]) / den
        return out
    patched.tag = tag
    return patched


def wrong_column_pair_reader():
    """A reader that uses the SECOND and THIRD columns instead of the first
    two, with the registered 9/8 weights.  The registered section 9 arm alone
    cannot distinguish some weight errors; it must distinguish this one."""
    real = read_plane_quantities

    def patched(mesh, planes, T, Uz, nz):
        out = real(mesh, planes, T, Uz, nz)
        for p, o in zip(planes, out):
            i1, i2 = p["idx"][1], p["idx"][2]
            o["Tc"] = (9.0 * T[i1] - T[i2]) / 8.0
            o["wc"] = (9.0 * Uz[i1] - Uz[i2]) / 8.0
        return out
    patched.tag = "wrong column pair (idx 1,2 instead of 0,1)"
    return patched


def make_synthetic_case(root, level, end_time, n_exec=None, end_name=None,
                        with_end_line=True, stale_fields=False,
                        rc="0", ranks="1"):
    """A minimal case tree for the completion checker to be tested against.

    The time directory name is built here by a LOCAL route ("%g" of the value)
    while check_completion RESOLVES it by scanning the disk -- deliberately
    two different routes, so this fixture and that resolver do not share one
    assumption (the L-321 shape).
    """
    case = os.path.join(root, "T8_MTT_" + level)
    os.makedirs(os.path.join(case, "system"), exist_ok=True)
    with open(os.path.join(case, "system", "controlDict"), "w") as fh:
        fh.write("application buoyantBoussinesqSimpleFoam;\nendTime %d;\n"
                 % end_time)
    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write("level %s\nendTime %d\nnProcs 1\nnz 4\nnr_blocks 2/2\n"
                 "n_cells_expected 16\n" % (level, end_time))
    os.makedirs(os.path.join(case, "0"), exist_ok=True)
    for f in FIELDS_REQUIRED:
        open(os.path.join(case, "0", f), "w").write("x\n")
    os.utime(os.path.join(case, "0", "T"), (1000.0, 1000.0))
    name = end_name if end_name is not None else ("%g" % end_time)
    for t in ("%g" % (end_time / 2.0), name):
        d = os.path.join(case, t)
        os.makedirs(d, exist_ok=True)
        for f in FIELDS_REQUIRED:
            p = os.path.join(d, f)
            open(p, "w").write("y\n")
            os.utime(p, (900.0, 900.0) if stale_fields else (2000.0, 2000.0))
    ne = n_exec if n_exec is not None else end_time
    with open(os.path.join(case, "log.solve"), "w") as fh:
        for i in range(ne):
            fh.write("ExecutionTime = %d s\n" % i)
        if with_end_line:
            fh.write("End\n")
    with open(os.path.join(root, "STATUS.T8_MTT_" + level), "w") as fh:
        fh.write("case=T8_MTT_%s\nrc=%s\nwall_s=10\nranks=%s\ncore_min=0.167\n"
                 "cap_core_min=%d\ntimeout_s=%d\n"
                 % (level, rc, ranks, CAP_CORE_MIN[level],
                    REGISTERED_TIMEOUT_S[level]))
    return case


def selftest():
    n_ok = n_bad = 0

    def ok(cond, what):
        nonlocal n_ok, n_bad
        if cond:
            n_ok += 1
            print("  ok    %s" % what)
        else:
            n_bad += 1
            print("  FAIL  %s" % what)

    hr("--selftest")

    print("(i) the registered constants reproduce from the document")
    ok(abs(SCALE - math.pi / (math.sin(WEDGE_HALF_RAD) *
                              math.cos(WEDGE_HALF_RAD))) < 1e-12,
       "SCALE: 2pi/sin(5 deg) == pi/(sin th cos th) to 1e-12")
    ok(abs(SCALE - 72.09146648398465) < 1e-9,
       "SCALE = 72.09146648 (the document's printed 72.0928 is a rounding "
       "error of 1.85e-5, larger than its own 1e-6 tolerance)")
    for lv in LEVELS:
        ok(CAP_CORE_MIN[lv] * 60 // RANKS == REGISTERED_TIMEOUT_S[lv],
           "level %s: cap %d core-min * 60 / %d rank = %d s, the registered "
           "timeout" % (lv, CAP_CORE_MIN[lv], RANKS, REGISTERED_TIMEOUT_S[lv]))
    ok(RANKS == 1, "ranks == 1 asserted explicitly (section 6 R5)")
    for lv, cells, steps in (("c", 6400, 8000), ("m", 25600, 12000),
                             ("f", 102400, 20000)):
        pred = cells * steps / 1.196e5 / 60.0
        ok(abs(pred - PREDICTED_CORE_MIN[lv]) < 0.01,
           "level %s: %d cells x %d steps / 1.196e5 = %.2f core-min "
           "(registered %.2f)" % (lv, cells, steps, pred,
                                  PREDICTED_CORE_MIN[lv]))
    ok(len(STATIONS_ZD) == 31 and STATIONS_ZD[0] == 10.0 and
       STATIONS_ZD[-1] == 25.0, "31 graded stations, z/D 10.0 to 25.0")
    ok(len(C5_STATIONS_ZD) == 41 and C5_STATIONS_ZD[-1] == 30.0,
       "41 C5 stations, z/D 10.0 to 30.0")

    print("")
    print("(ii) the Roache triple -- every state, and the CORRECT Richardson "
          "sign against a closed-form case")
    g = gci_triple(1.16, 1.04, 1.01)
    ok(g["state"] == "CONVERGING", "1.16/1.04/1.01 at r=2 is CONVERGING")
    ok(abs(g["order"] - 2.0) < 1e-12, "observed order recovers p = 2 exactly")
    # this ladder IS a power law with limit 1.0 by construction:
    #   f(h) = 1 + 0.16 h^2 with h = 1, 1/2, 1/4  ->  1.16, 1.04, 1.01
    ok(abs(g["richardson"] - 1.0) < 1e-12,
       "richardson = f_fine - e21/den recovers the KNOWN limit 1.0 to 1e-12 "
       "(N-T8: a VALUE control, not a key-exists check)")
    ok(abs(g["richardson_parent_convention"] - 1.02) < 1e-12,
       "the parents' '+' form returns 1.02 -- wrong, and named as such")
    ok(abs(g["richardson"] + g["richardson_parent_convention"]
           - 2.0 * 1.01) < 1e-12,
       "structural identity richardson + parent_convention == 2*f_fine")
    # --- state fixtures, each with its own p stated ----------------------
    # CORRECTED 2026-08-25.  Three fixtures here were MIS-SPECIFIED when this
    # file was first written, and the CLASSIFIER WAS NOT AT FAULT:
    #   (1.05, 1.02, 1.00): e21 = 0.02, e32 = 0.03, ratio = 1.5,
    #       p = ln 1.5 / ln 2 = +0.5850, which is above STAGNANT_FLOOR and so
    #       is CONVERGING -- correctly.  A DIVERGENT triple needs the error to
    #       GROW under refinement, i.e. 0 < ratio < 1 giving p <= 0.
    #   (1.06375, 1.03375, 1.0): e21 = 0.03375, e32 = 0.03, ratio = 0.8889,
    #       p = -0.1699 -> DIVERGENT, not STAGNANT.  The intended median was
    #       1.03 (ratio 1.125, p = +0.1699), which is 0 < p < 0.5.
    #   The third failure ("no GCI on a DIVERGENT triple") was a CONSEQUENCE
    #       of the first: that triple really was CONVERGING, so it really did
    #       carry a GCI, and the assertion was reading a correct refusal as a
    #       leak.
    # Before any edit, gci_triple was checked branch-for-branch against the
    # lab canon scripts/roache_triple.py:gci_equal (tracked in HEAD, written
    # independently of this file) and MATCHES it: EXACT -> OSCILLATORY on
    # ratio < 0 -> DIVERGENT on p <= 0 -> STAGNANT on p < STAGNANT_FLOOR = 0.5
    # -> CONVERGING, with the same corrected Richardson sign.  Only the test
    # fixtures below were changed; gci_triple itself is UNTOUCHED.
    TRIPLE_FIXTURES = {
        "DIVERGENT":   (1.07, 1.05, 1.00),      # ratio 0.400, p = -1.3219
        "STAGNANT":    (1.06375, 1.03, 1.00),   # ratio 1.125, p = +0.1699
        "OSCILLATORY": (1.05, 1.10, 1.00),      # ratio < 0, no order formed
        "EXACT":       (1.05, 1.00, 1.00),      # e21 == 0, no order formed
    }
    for _st in ("DIVERGENT", "STAGNANT", "OSCILLATORY", "EXACT"):
        ok(gci_triple(*TRIPLE_FIXTURES[_st])["state"] == _st,
           "%s triple classified" % _st)
    for _st in ("DIVERGENT", "STAGNANT", "OSCILLATORY", "EXACT"):
        tr = gci_triple(*TRIPLE_FIXTURES[_st])
        ok(tr["GCI_pct"] is None and tr["GCI_abs"] is None
           and tr["richardson"] is None,
           "NO GCI and NO Richardson quoted on a %s triple "
           "(CLAUDE.md rule 5)" % _st)

    # The STAGNANT floor is a REAL boundary, bracketed either side.  The
    # knife edge p == 0.5 is NOT asserted: constructing it in floating point
    # lands at 0.49999999999999872, so an assertion there would be testing
    # float noise, not the rule.
    ok(gci_triple(1.03 + 0.03 * (2.0 ** 0.4), 1.03, 1.00)["state"]
       == "STAGNANT", "p = 0.4 (below STAGNANT_FLOOR = 0.5) is STAGNANT")
    ok(gci_triple(1.03 + 0.03 * (2.0 ** 0.6), 1.03, 1.00)["state"]
       == "CONVERGING", "p = 0.6 (above STAGNANT_FLOOR = 0.5) is CONVERGING")

    # Differential cross-check against the lab canon.  This is a SELFTEST-only
    # comparison and does NOT put the canon on the grading path: section 12 S5
    # forbids this comparator INHERITING a GCI routine (specifically
    # analyse_t1c.py / analyse_t3.py, for their wrong Richardson sign), and
    # nothing here imports one into grade().  If the canon is unavailable the
    # check is SKIPPED and says so rather than silently passing.
    _canon = None
    try:
        _cs = os.path.join(REPO, "scripts")
        if _cs not in sys.path:
            sys.path.insert(0, _cs)
        import roache_triple as _canon
    except Exception as _e:
        print("  SKIP  canon differential: scripts/roache_triple.py not "
              "importable (%s) -- NOT counted as a pass" % _e.__class__.__name__)
    if _canon is not None and hasattr(_canon, "gci_equal"):
        _sweep = [(1.16, 1.04, 1.01), (1.07, 1.05, 1.00),
                  (1.06375, 1.03, 1.00), (1.05, 1.10, 1.00),
                  (1.05, 1.00, 1.00), (1.05, 1.02, 1.00),
                  (1.06375, 1.03375, 1.00), (2.0, 1.5, 1.25),
                  (0.9, 0.95, 1.00), (-1.0, -0.5, -0.25)]
        _bad = []
        for _t in _sweep:
            _mine = gci_triple(*_t)["state"]
            try:
                _theirs = _canon.gci_equal(_t[0], _t[1], _t[2],
                                           r=R_REFINE, fs=FS, dim=DIM)["state"]
            except TypeError:
                _theirs = _canon.gci_equal(_t[0], _t[1], _t[2])["state"]
            if _mine != _theirs:
                _bad.append((_t, _mine, _theirs))
        ok(not _bad,
           "canon differential: gci_triple agrees with "
           "scripts/roache_triple.gci_equal on all %d triples%s"
           % (len(_sweep),
              "" if not _bad else " -- DISAGREES: %r" % (_bad,)))

    print("")
    print("(iii) the gate is one-way, and criterion (1) fires BEFORE the "
          "triple is classified")
    conv_good = {lv: dict(state="CONVERGED") for lv in LEVELS}
    conv_bad = {"c": dict(state="CONVERGED"), "m": dict(state="NOT_CONVERGED"),
                "f": dict(state="CONVERGED")}
    r_pass = grade_row("n_w", {"c": -0.36, "m": -0.34, "f": -0.335},
                       conv_good, "")
    ok(r_pass["verdict"] == VERDICT_PASS, "in-band CONVERGING row is PASS")
    r_nar = grade_row("n_w", {"c": -0.36, "m": -0.34, "f": -0.335},
                      conv_bad, "")
    ok(r_nar["verdict"] == VERDICT_NAR and r_nar["band"] == VERDICT_PASS,
       "the SAME in-band row becomes NOT A RESULT when one level is not "
       "converged -- the VMFL051 shape: a comfortable deviation is not "
       "evidence about the levels")
    ok(r_nar["triple"] is None,
       "criterion (1) fired BEFORE the triple was classified at all")
    r_osc = grade_row("n_w", {"c": -0.36, "m": -0.30, "f": -0.335},
                      conv_good, "")
    ok(r_osc["verdict"] == VERDICT_NAR and r_osc["band"] == VERDICT_PASS,
       "an in-band row on an OSCILLATORY triple is NOT A RESULT")
    r_fail = grade_row("n_w", {"c": -0.60, "m": -0.50, "f": -0.45},
                       conv_good, "")
    ok(r_fail["band"] == VERDICT_FAIL,
       "an out-of-band fine value is GATE FAIL")
    # the one-way property, exhaustively over the reachable combinations
    oneway = True
    for cbl in (conv_good, conv_bad):
        for vals in ({"c": -0.36, "m": -0.34, "f": -0.335},
                     {"c": -0.36, "m": -0.30, "f": -0.335},
                     {"c": -0.60, "m": -0.50, "f": -0.45},
                     {"c": -0.60, "m": -0.50, "f": -0.50}):
            rr = grade_row("n_w", vals, cbl, "")
            if rr["verdict"] not in (rr["band"], VERDICT_NAR):
                oneway = False
    ok(oneway, "over every combination tried, the verdict is either the band "
               "verdict or NOT A RESULT -- never the reverse direction")

    print("")
    print("(iv) the exponent fit recovers a KNOWN power law exactly")
    z0 = 0.05
    st = dict(z=[], zD=[], wc=[], dT=[], Q=[], b=[])
    for zd in STATIONS_ZD:
        z = zd * D_SOURCE
        zz = z - z0
        st["z"].append(z)
        st["zD"].append(zd)
        st["wc"].append(2.5 * zz ** (-1.0 / 3.0))
        st["dT"].append(7.0 * zz ** (-5.0 / 3.0))
        st["Q"].append(0.3 * zz ** (+5.0 / 3.0))
        st["b"].append(0.1 * (z - z0))
    fx = fit_exponents(st, z0)
    ok(abs(fx["n_w"] - (-1.0 / 3.0)) < 1e-12, "n_w recovered to 1e-12")
    ok(abs(fx["n_T"] - (-5.0 / 3.0)) < 1e-12, "n_T recovered to 1e-12")
    ok(abs(fx["n_Q"] - (+5.0 / 3.0)) < 1e-12, "n_Q recovered to 1e-12")
    rad = fit_radius(st)
    ok(abs(rad["z0"] - z0) < 1e-12, "the b(z) fit recovers z0 to 1e-12")
    ok(abs(rad["alpha"] - (5.0 / 6.0) * 0.1) < 1e-12,
       "alpha = (5/6) s recovered to 1e-12")

    print("")
    print("(v) the centreline extrapolation is the registered instrument")
    #  a field exactly quadratic in r, sampled at r1 and r2 = 3 r1.
    #  THESE THREE ARE ARITHMETIC IDENTITIES ONLY.  They re-derive the formula
    #  and so cannot see a change to the SHIPPED weights; the checks that DO
    #  call the shipped reader follow immediately below (amendment A1).
    a, b_, r1 = 3.0, -0.5, 0.0125
    f1 = a + b_ * r1 ** 2
    f2 = a + b_ * (3.0 * r1) ** 2
    ok(abs((9.0 * f1 - f2) / 8.0 - a) < 1e-14,
       "IDENTITY ONLY: (9 f1 - f2)/8 recovers the axis value of a "
       "quadratic-in-r field exactly, with r2 = 3 r1")
    ok(abs(((9.0 * (f1 + PLANT) - (f2 + PLANT)) / 8.0) - (a + PLANT)) < 1e-14,
       "IDENTITY ONLY: shifting BOTH columns by PLANT shifts the extrapolate "
       "by exactly PLANT -- the section 9 response is analytic, not approximate")
    ok(abs(((9.0 * (f1 + PLANT) - f2) / 8.0) - (a + 9.0 * PLANT / 8.0)) < 1e-14,
       "IDENTITY ONLY: shifting the INNERMOST column only shifts it by exactly "
       "9*PLANT/8 -- supplementary arm (a) distinguishes a wrong column pair")

    # -- amendment A1: the SHIPPED reader, CALLED, on a real case on disk ----
    tmp5 = tempfile.mkdtemp(prefix="t8_reader_")
    try:
        root5, meta = make_synthetic_field_case(tmp5)
        mesh = read_mesh(root5, "100")
        ok(mesh is not None and mesh["n"] == meta["nz"] * meta["nr"],
           "read_mesh CALLED: %d cells off a real endTime directory"
           % (mesh["n"] if mesh else -1))
        planes, why5 = resolve_planes(mesh, meta["nz"], meta["nr"])
        ok(planes is not None and len(planes) == meta["nz"],
           "resolve_planes CALLED: %d planes, r2/r1 = 3 accepted (%s)"
           % (len(planes) if planes else -1, why5))
        Tf = read_internal(os.path.join(root5, "100", "T"))
        Uf = read_internal(os.path.join(root5, "100", "U"), vector=True)
        pq = read_plane_quantities(mesh, planes, Tf, [u[2] for u in Uf],
                                   meta["nz"])
        worstT = max(abs(pq[k]["Tc"] - meta["axis_T"][k])
                     for k in range(meta["nz"]))
        worstw = max(abs(pq[k]["wc"] - meta["axis_w"][k])
                     for k in range(meta["nz"]))
        # 1e-9 is float-noise headroom on values of order 300 K, not a fitted
        # number: the mis-weightings this must catch are 4 % errors.
        ok(worstT < 1e-9,
           "read_plane_quantities CALLED: the SHIPPED Tc reproduces the "
           "analytic axis value at all %d planes, worst %.3e K"
           % (meta["nz"], worstT))
        ok(worstw < 1e-9,
           "read_plane_quantities CALLED: the SHIPPED wc reproduces the "
           "analytic axis value at all %d planes, worst %.3e m/s"
           % (meta["nz"], worstw))
        st5, why5 = read_stations(pq, STATIONS_ZD)
        ok(st5 is not None and len(st5["zD"]) == len(STATIONS_ZD),
           "read_stations CALLED: all %d registered stations resolved (%s)"
           % (len(STATIONS_ZD), why5))
        # THE NEGATIVE ARM for ruling 1: a mis-weighted SHIPPED extrapolation
        # must be visible to this same comparison.
        _saved = read_plane_quantities
        try:
            globals()["read_plane_quantities"] = mis_weighted_reader(
                7.0, 1.0, 6.0, "(7 f1 - f2)/6")
            pqm = read_plane_quantities(mesh, planes, Tf,
                                        [u[2] for u in Uf], meta["nz"])
            worstm = max(abs(pqm[k]["Tc"] - meta["axis_T"][k])
                         for k in range(meta["nz"]))
            ok(worstm > 1e-6,
               "NEGATIVE ARM FIRES: a (7 f1 - f2)/6 extrapolation misses the "
               "analytic axis value by %.3e K -- this check, unlike the three "
               "identities above, CAN see a change to the shipped weights"
               % worstm)
        finally:
            globals()["read_plane_quantities"] = _saved
    finally:
        shutil.rmtree(tmp5, ignore_errors=True)

    print("")
    print("(vi) the completion checker is SHOWN ABLE TO FIRE on every clause")
    tmp = tempfile.mkdtemp(prefix="t8_selftest_")
    try:
        case = make_synthetic_case(tmp, "c", 40)
        good, why, _ = check_completion(case, "c", tmp)
        ok(good, "a complete synthetic case passes (the non-zero control: a "
                 "checker never shown able to PASS is as useless as one never "
                 "shown able to fail)")
        for label, kw in (("rc != 0", dict(rc="1")),
                          ("ranks != 1", dict(ranks="4")),
                          ("no End line", dict(with_end_line=False)),
                          ("ExecutionTime count != endTime", dict(n_exec=39)),
                          ("last time != endTime", dict(end_name="39")),
                          ("age guard: fields older than 0/T",
                           dict(stale_fields=True))):
            sub = tempfile.mkdtemp(prefix="t8_selftest_", dir=tmp)
            c2 = make_synthetic_case(sub, "c", 40, **kw)
            g2, why2, _ = check_completion(c2, "c", sub)
            ok(not g2, "REFUSES on %-34s (%s)" % (label, why2[:44]))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("(vii) the field reader survives a round trip through the planting "
          "writer")
    tmp = tempfile.mkdtemp(prefix="t8_selftest_")
    try:
        src = os.path.join(tmp, "T")
        with open(src, "w") as fh:
            fh.write("FoamFile{}\ninternalField   nonuniform List<scalar>\n"
                     "3\n(\n1.0\n2.0\n3.0\n)\n;\n\nboundaryField{}\n")
        dst = os.path.join(tmp, "T2")
        write_internal(src, dst, [1.5, 2.5, 3.5], vector=False)
        got = read_internal(dst)
        ok(got == [1.5, 2.5, 3.5], "scalar internalField round trip")
        srcv = os.path.join(tmp, "U")
        with open(srcv, "w") as fh:
            fh.write("FoamFile{}\ninternalField   nonuniform List<vector>\n"
                     "2\n(\n(1 2 3)\n(4 5 6)\n)\n;\n\nboundaryField{}\n")
        dstv = os.path.join(tmp, "U2")
        write_internal(srcv, dstv, [(1.0, 2.0, 3.5), (4.0, 5.0, 6.5)],
                       vector=True)
        gotv = read_internal(dstv, vector=True)
        ok(gotv == [(1.0, 2.0, 3.5), (4.0, 5.0, 6.5)],
           "vector internalField round trip")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("")
    print("(viii) the section 12 S6 exit contract is representable")
    ok(sorted({0, 1, 2, 3}) == [0, 1, 2, 3],
       "0 all PASS / 1 any GATE FAIL / 2 REFUSE / 3 fewer than three rows "
       "reached the band -- NON-ZERO by construction, answering D522")

    print("")
    print("(ix) the plateau conjunct is DECLARED, not defaulted")
    ok(PLATEAU_MAX_EXPONENT_DRIFT is None,
       "PLATEAU_MAX_EXPONENT_DRIFT is None and the grading output SAYS SO: "
       "section 7's 'and plateaued' has no separately registered criterion in "
       "T8 and this file does not invent one")

    # -- amendment A1, 2026-08-25 -------------------------------------------
    print("")
    print("(x) THE SECTION 9 PLANTED ZERO IS SHOWN ABLE TO FIRE "
          "(CLAUDE.md rule 3, applied to this file's own control)")
    tmpx = tempfile.mkdtemp(prefix="t8_plantctl_")
    try:
        rootx, mx = make_synthetic_field_case(tmpx)
        good, reason, plines = check_planted_zero(rootx, "100",
                                                  mx["nz"], mx["nr"])
        ok(good and len(plines) == 6,
           "check_planted_zero CALLED on a real case on disk: all %d arms "
           "PASS on an intact reader (%s)" % (len(plines), reason))
        for _state, _name, _detail in plines:
            ok(_state == "PASS", "  arm PASSES on an intact reader: " + _name)

        # NEGATIVE ARM 1 -- a mis-weighted extrapolation.
        _saved = read_plane_quantities
        try:
            globals()["read_plane_quantities"] = mis_weighted_reader(
                7.0, 1.0, 6.0, "(7 f1 - f2)/6")
            bad_ok, bad_why, bad_lines = check_planted_zero(
                rootx, "100", mx["nz"], mx["nr"])
        finally:
            globals()["read_plane_quantities"] = _saved
        ok(bad_ok is False,
           "NEGATIVE ARM FIRES: with a (7 f1 - f2)/6 extrapolation the "
           "planted zero REFUSES -- " + bad_why)
        reg = [l for l in bad_lines if "registered" in l[1]]
        sup_a = [l for l in bad_lines if "supplementary (a)" in l[1]]
        ok(len(sup_a) == 2 and all(l[0] == "FAIL" for l in sup_a),
           "and it is SUPPLEMENTARY ARM (a) that catches it: both (a) arms "
           "FAIL")
        ok(len(reg) == 2 and all(l[0] == "PASS" for l in reg),
           "while BOTH REGISTERED ARMS PASS -- because (7-1)/6 = 1 exactly, "
           "so a both-column plant shifts by PLANT under the WRONG weights "
           "too.  The supplementary arm is LOAD-BEARING, not decoration, and "
           "this is the measurement that proves it")

        # NEGATIVE ARM 2 -- the right weights on the wrong pair of columns.
        _saved = read_plane_quantities
        try:
            globals()["read_plane_quantities"] = wrong_column_pair_reader()
            bad2_ok, bad2_why, _ = check_planted_zero(
                rootx, "100", mx["nz"], mx["nr"])
        finally:
            globals()["read_plane_quantities"] = _saved
        ok(bad2_ok is False,
           "NEGATIVE ARM FIRES: registered weights on the WRONG column pair "
           "(idx 1,2) REFUSES -- " + bad2_why)
    finally:
        shutil.rmtree(tmpx, ignore_errors=True)

    hr("--selftest: %d ok, %d FAILED" % (n_ok, n_bad))
    return 0 if n_bad == 0 else 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--check-freeze", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check_freeze:
        hr("section 11 -- freeze set hashed against the committed blob")
        good, lines = check_freeze_set()
        for ln in lines:
            print(ln)
        print("  -> " + ("FROZEN" if good else "NOT FROZEN"))
        return 0 if good else 2
    return grade(os.path.abspath(a.root))


if __name__ == "__main__":
    sys.exit(main())
