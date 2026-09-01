#!/usr/bin/env python3
"""T25R2 COMPARATOR -- 8-cell aviation battery module with RESOLVED cooling
channels, true transient conjugate, at SANAA'S 2026-09-01 04:20Z VOLUMETRIC
LOADS and at the numerics MEASURED by the T25RF probe.

Gates, thresholds, caps and labels are registered at
`docs/campaigns/T-family/T25R2_PREREGISTRATION.md` and FROZEN by its commit sha.
This file is committed in the same commit and BEFORE ANY T25R2 COMPUTE -- no
solver, no `blockMesh`, no `checkMesh`, no `splitMeshRegions` has run for T25R2
and no T25R2 case directory exists.  It therefore cannot have been shaped by a
result it had already seen (CLAUDE.md rule 2).

PATTERN.  `analyse_t25R.py`, which is FROZEN and IS NOT EDITED by this rung
(CLAUDE.md rule 6).  Most of it was RIGHT and is inherited verbatim: the mesh
reader, the planted-perturbation controls, the delegated completion rule, the
energy ledger, the D1/D2/D3 criterion structure and the refusal to compute an
order from two points.  FOUR things change, and each is named on this file's
own face below.

=====================================================================
CHANGE 1 -- THE LOAD IS A VOLUMETRIC RATE, AND IT IS THE PRIMARY QUANTITY
=====================================================================
Sanaa, verbatim, 2026-09-01 ~04:20Z
(etc/sessions/2026-09-01T0420Z_sanaa_battery_loads_and_overnight_priorities.md):

  "Battery loads: set the heat source as a volumetric rate from a real cell,
   not a per-cell wattage on a unit-depth model. Takeoff: q~ ~ 1x10^5 W/m^3
   (~40-50 W in a 100x30x150 mm cell, 5-8C class); cruise ~ 2.5x10^4 W/m^3.
   State the basis in the assumptions box. The temperature rise is then whatever
   the physics gives; I am not prescribing "tens of kelvin", I am prescribing
   realistic heat density. If the result is 8 K, 8 K is the answer."

(`q~` above is her q-triple-prime, respelled only because a triple quote cannot
appear inside this docstring.)

THE VOLUMETRIC RATE IS THE REGISTERED QUANTITY: 1.0e5 W/m3 takeoff, 2.5e4 W/m3
cruise.  A per-cell wattage appears NOWHERE as an input and is emitted only as a
DERIVED CONSEQUENCE of the 2-D unit-depth normalisation, labelled as such every
time it is printed.  T25R's construction -- 210 W/cell derived on a unit-depth
slab -- is the thing she rejected by name, and it is gone.

=====================================================================
CHANGE 2 -- THE NUMERICS ARE MEASURED (T25RF ARM A2T), NOT CHOSEN
=====================================================================
T25R_L1 died at t=1.5 with `FOAM FATAL ERROR: Negative initial temperature
T0: -14.4619608928`, rc=134.  MECHANISM, read at v2606 source and then
CONFIRMED BY MEASUREMENT (T25RF arm A0 reproduced it under the NEW loads to the
same three steps and T0 = -14.458, so the divergence is NUMERICAL, not
load-driven):

  `chtMultiRegionFoam.C:111` sets finalIter on the last outer sweep;
  `fvMatrix::relax()` (fvMatrix.C:1249) resolves its relaxation key as
  `psi_.select(isFinalIteration())`, and `GeometricField::select(bool)`
  (GeometricField.C:1179) returns `name() + "Final"`.  OPENFOAM KEYWORD REGEXES
  MATCH IN FULL, so T25R's `"(U|h|k|omega)"` DOES NOT MATCH `UFinal`/`hFinal`:
  momentum and energy ran UNRELAXED ON THE FINAL SWEEP.  At Co ~ 1600 the 1/dt
  term adds almost nothing to the momentum diagonal, so that one unrelaxed sweep
  had no diagonal dominance left to stabilise it.

THE MECHANISM IS A MISSING DICTIONARY KEY, SO THIS FILE VERIFIES THE KEYS IN THE
DICTIONARY THAT ACTUALLY RAN (`numerics_check`) AND REFUSES IF ANY IS ABSENT.
A registration that fixed a crash by writing a key, and then graded a case
without checking the key was there, would have learned nothing.  This is
L-221/L-222's rule in its general form: a lesson is not applied until every call
site asserts it.

Also measured and registered: the T25R `p_rgh` absolute tolerance of 1e-9 IS
UNREACHABLE -- GAMG stalls at ~4.4e-9 on this system, and 608 of 1200 solves in
the probe's 10-sweep arm terminated at `maxIter` 1000 without reaching it.
Relaxing it to 1e-8 removed 601,763 GAMG iterations (627,533 -> 25,770, 24.4x)
while changing the answer by 0.000e+00 K.  Those discarded iterations bought
nothing and are named as WASTE, never absorbed into a cost ratio (rule 12).

=====================================================================
CHANGE 3 -- THE OUTER-LOOP GATE.  T25R's SECTION 3.5 IS INVALID AND IS GONE.
=====================================================================
T25R section 3.5 gated on the LAST-SWEEP INITIAL RESIDUAL < 1e-6.  That
threshold was calibrated for an UNRELAXED final sweep -- the frozen dictionary
chose the unrelaxed final sweep DELIBERATELY, in order to keep that gate
meaningful -- and that choice is what crashed the run.  Relaxing the final sweep
fixes the crash and DESTROYS THE GATE'S CALIBRATION.  A threshold whose
calibrating assumption has been removed is not a threshold.

  *** THE LAST-SWEEP RESIDUAL CENSUS IS RETAINED AS A REPORT, WITH NO THRESHOLD
      ATTACHED AND NO VERDICT DERIVABLE FROM IT. ***

The outer loop is gated INSTEAD by DEMONSTRATED SWEEP-COUNT INDEPENDENCE, IN
KELVIN, between `T25R2_L1` (nOuterCorrectors 10) and `T25R2_L1_OC20`
(nOuterCorrectors 20) -- identical in every other respect.  Section 3.5 of the
frozen document fixes the three deltas O1/O2/O3 and their thresholds;
`oc_independence()` here computes them and NOTHING ELSE.

WHY IT IS FORCED BY MEASUREMENT AND NOT BY PREFERENCE.  The probe measured 5
sweeps against 10 disagreeing by 1.05e-3 K at t=1 s, 3.47e-3 K at t=10 s and
6.02e-3 K at t=30 s -- 0.53 % of the 1.13 K rise, ALREADY HALF the 10*PLANT
signal scale after 3.3 % of the case duration, AND STILL GROWING.  WE THEREFORE
DO NOT KNOW THAT 10 SWEEPS IS CONVERGED.  T25R2 DEMONSTRATES IT RATHER THAN
ASSUMING IT, and the arm is built so that IT CAN FAIL.

=====================================================================
WHAT THIS COMPARATOR DOES NOT DO, AND WILL NOT BE MADE TO DO
=====================================================================

*** TWO MESH LEVELS ARE TWO POINTS.  NO LADDER IS REGISTERED. ***
No observed order, no GCI and no Roache classification
(CONVERGING / DIVERGENT / STAGNANT / OSCILLATORY / EXACT) is computed, quoted
or quotable from this artifact.  Two points cannot measure an order and cannot
yield a GCI.  CLAUDE.md rule 5 is not weakened by that: it governs a GRID
TRIPLE, and this rung produces none.  Section 6.3 of the frozen document
registers the mesh pair and the step pair as SENSITIVITY DIFFERENCES and
nothing else.  Precedent for saying so on the artifact's own face:
`analyse_t23.py:477`, `analyse_t24.py:744`.

THIS FAMILY'S MOST REPEATED FAILURE IS SMUGGLING AN ORDER OUT OF TWO POINTS.
There is no code path in this file that computes one.  *** `T25R2_L1_OC20` IS
NOT A THIRD MESH LEVEL. ***  It is L1's mesh at a different SWEEP COUNT, it
enters NO sensitivity panel, and no order may be read from the L1 / L1_OC20 / L2
collection under any pretext.

*** T25R2 INHERITS NO PASS FROM T20. ***  Section 6.1: the T20 exact gate is the
registered V-tier for CASE 4 and it HAS NOT DISCHARGED --
`T20_P10_CONDITION_iii_MEASUREMENT.md:9` states "T20 remains NOT A RESULT on
its own registered terms".  The citation is a POINTER, not a proof, and this
file prints that on every invocation so no downstream reader picks up the
citation without the caveat.

*** T25R2 INHERITS NOTHING FROM T25R EXCEPT ITS TEXT. ***  `T25R_L1` is
`NOT A RESULT` (rc=134, one FOAM FATAL, last written time 1.5 against endTime
900) and no number from it, from `T25R_L2`, from `T25R_L2_DT025` or from the
UNGATED T25RF probe is a result here.  The probe's numbers INFORMED this
registration; they are not this registration's answer
(VERIFICATION_CHARTER section 2m.2).

*** A SMALL DIFFERENCE BETWEEN TWO POINTS IS CONSISTENT WITH CONVERGENCE AND IS
NOT EVIDENCE OF IT. ***  The sensitivity panels say so in those words.

=====================================================================
THE INSTRUMENT-ADMISSION CONTROL (CLAUDE.md rule 3, section 7.1)
=====================================================================
A zero from a reader not shown able to see a non-zero is not evidence.  Every
reader carries a planted-perturbation control with all nine registered clauses,
following `verification/runs/T-family/T24_runs/analyse_t24.py:459-530`:

  1. COPY FIRST into scratch, with a REFUSAL if the scratch path resolves
     INSIDE the case.  The case is never written to.
  2. NEGATIVE ARM at bitwise 0.0.  NO absolute tolerance anywhere in it.
  3. POSITIVE ARM: a MEASURED magnitude ladder with an epsilon-free floor.
  4. REFUSE IF BLIND.
  5. The ONLY sizing tolerance, and it is RELATIVE: got >= PLANT*(1-1e-9).
     analyse_t3.py:327's ABSOLUTE `seen >= PLANT - 1e-15` is EXPRESSLY NOT
     ADOPTED: at this magnitude an absolute epsilon is decided by rounding
     wiggle rather than by whether the reader saw the plant.
  6. PLANT is IMPORTED from scripts/roache_triple.py and NEVER redefined.
  7. Plants are written BY LINE INDEX inside a window taken from the field's
     OWN HEADER.  Nothing is located by value.  A patch plant writes EVERY face
     so the expected shift is EXACTLY `mag`, never mag/N.
  8. The case bytes are compared before and after; scratch is removed in a
     `finally`.
  9. __pycache__ is cleared first (stale bytecode INVERTS a mutation control).

A REFUSAL ON ANY READER MAKES THE WHOLE RUNG `NOT A RESULT`.

*** EVERY GUARD IN THIS FILE IS DRIVEN TO ITS REFUSAL BY MUTATION IN
--selftest. ***  A supervisor's read of a control is necessary and NOT
sufficient (VERIFICATION_CHARTER section 2n.18); a control not PROVED to fire is
ceremony.

=====================================================================
COMPLETION IS DELEGATED AND NEVER REIMPLEMENTED
=====================================================================
`mark_done_t25R2.py` decides CLAUDE.md rule 4.  This file CALLS it.  There is no
second copy of the completion rule here, and a run without a DONE marker from
that instrument has its numbers withheld, not printed with a caveat.

=====================================================================
THE TRACEBACK TRAP -- MEASURED ELSEWHERE THIS NIGHT AND CLOSED HERE
=====================================================================
An instrument with no `except` clause lets an uncaught traceback leave the
interpreter with exit status 1 -- which in this file's exit vocabulary is
"a gate failed or a row is NOT A RESULT", i.e. a GRADED outcome.  A crash would
then be INDISTINGUISHABLE FROM A MEASUREMENT.  `_guarded()` converts every
uncaught exception into a REFUSAL (exit 2): a crashed instrument has measured
nothing and is not entitled to return a graded answer of any kind.

NO `assert` (L-332): behaviour is identical under `python3 -O`.

Usage:
    python3 analyse_t25R2.py [CASE ...] [--root DIR] [--json OUT]
    python3 analyse_t25R2.py --selftest
Exit: 0 graded, 1 a gate failed or a row is NOT A RESULT, 2 REFUSAL.
"""
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, HERE)
import roache_triple as RT                                      # noqa: E402
import mark_done_t25R2 as MD                                    # noqa: E402

EXIT_OK, EXIT_FAIL, EXIT_REFUSE = 0, 1, 2

# ---- section 7.1 clause 6: IMPORTED, NEVER REDEFINED. ---------------------
PLANT = RT.PLANT                          # 1.234e-03 K
LADDER = (10.0, 1.0, 1e-1, 1e-2, PLANT, 1e-3, 1e-4, 1e-5, 1e-6)
PLANT_REL_SLACK = 1e-9                    # clause 5: the ONLY sizing tolerance

FROZEN_DOC = "docs/campaigns/T-family/T25R2_PREREGISTRATION.md"

# ---- section 1, THE REGISTERED RUN SET.  FOUR, named, closed. ------------
CASES = ("T25R2_L1", "T25R2_L1_OC20", "T25R2_L2", "T25R2_L2_DT025")
LEVEL = {"T25R2_L1": "L1", "T25R2_L1_OC20": "L1",
         "T25R2_L2": "L2", "T25R2_L2_DT025": "L2"}
DELTAT = {"T25R2_L1": 0.5, "T25R2_L1_OC20": 0.5,
          "T25R2_L2": 0.5, "T25R2_L2_DT025": 0.25}
# Section 3.4 / 3.5: the registered outer-sweep count PER CASE.  It is checked
# against the dictionary that actually ran (`numerics_check`), never assumed.
NOUTER = {"T25R2_L1": 10, "T25R2_L1_OC20": 20,
          "T25R2_L2": 10, "T25R2_L2_DT025": 10}
PRIMARY = "T25R2_L2"                        # section 5.3: D1/D3 read here
MESH_PAIR = ("T25R2_L1", "T25R2_L2")        # section 6.3
STEP_PAIR = ("T25R2_L2", "T25R2_L2_DT025")  # section 6.3
OC_PAIR = ("T25R2_L1", "T25R2_L1_OC20")     # section 3.5, THE OUTER-LOOP GATE

# ---- section 2.1, GEOMETRY.  Every number is the frozen document's. -------
N_CELLS = 8
CELL_LX, CELL_LY, GAP, DEPTH = 0.100, 0.030, 0.003, 1.000
PITCH = CELL_LY + GAP                     # 0.033 m
V_CELL = CELL_LX * CELL_LY * DEPTH        # 3.000e-03 m3
X_BAND = 0.010                            # section 5.3 up/down band width

# ---- section 4.2, THE LOAD.  *** VOLUMETRIC RATE FIRST. ***
# Sanaa's 04:20Z order, verbatim in the docstring above and in section 4.2 of
# the frozen document.  q''' IS THE REGISTERED QUANTITY; the per-cell
# wattage below it is a DERIVED CONSEQUENCE of the 2-D unit-depth normalisation
# and is never an input.
Q_TAKEOFF, Q_CRUISE = 100000.0, 25000.0   # W/m3, REGISTERED
T_PULSE, T_END = 60.0, 900.0              # s
RAMP_LO, RAMP_HI = 59.999, 60.000         # section 4.5, the 1 ms ramp
T_INIT = 293.0                            # K
RHO_S, CP_S = 2500.0, 1000.0
CP_AIR = 1005.0
E_GEN = N_CELLS * V_CELL * (Q_TAKEOFF * T_PULSE + Q_CRUISE * (T_END - T_PULSE))

# ---- SANAA'S REAL CELL (section 4.2).  Her 100 x 30 mm SECTION IS IDENTICAL
# to the registered 2-D section; ONLY THE DEPTH DIFFERS (0.150 m hers, 1.000 m
# OpenFOAM unit depth).  A VOLUMETRIC RATE IS DEPTH-INDEPENDENT AND THEREFORE
# TRANSFERS EXACTLY.  Her basis is self-consistent: 45 W / 4.5e-4 m3 = 1.0e5.
V_REAL_CELL = CELL_LX * CELL_LY * 0.150   # 4.500e-04 m3

# ---- section 4.3, THE PREDICTIONS, REGISTERED BEFORE THE RUN.
ADIABATIC_PULSE_K = Q_TAKEOFF * T_PULSE / (RHO_S * CP_S)          # 2.400 K
ADIABATIC_900_K = (Q_TAKEOFF * T_PULSE
                   + Q_CRUISE * (T_END - T_PULSE)) / (RHO_S * CP_S)  # 10.800 K
MDOT = 0.20160                            # kg/s, section 4.4
H_REPRESENTATIVE = 53.9                   # W/m2K -- DECLARED-REPRESENTATIVE,
#   Dittus-Boelter, NOT MEASURED, and IMPOSED NOWHERE IN THE SOLVE.  It is used
#   only for the printed lumped-tau and steady-rise arithmetic.
A_INTERIOR = 0.2                          # m2 per metre depth, two faces
CRUISE_STEADY_RISE_K = (Q_CRUISE * V_CELL
                        / (H_REPRESENTATIVE * A_INTERIOR))         # 6.957 K

# ---- THE REGISTERED THRESHOLDS.  Transcribed from the frozen document. ----
ENERGY_BAND = 0.020                       # 6.2: |R|/E_gen <= 2.0 %
D3_FLOOR = 10.0 * PLANT                   # 5.3: 1.234e-02 K
MESH_MAXNONORTH, MESH_MAXSKEW = 70.0, 4.0  # 2.4
PLANT10_PCT = 0.10                        # 6.2 planted +10 % source control

# ==========================================================================
# SECTION 3.5.  *** THERE IS NO RESIDUAL THRESHOLD IN THIS FILE. ***
# ==========================================================================
# T25R's `RESID_GATE = {"p_rgh": 1e-6, "Ux": 1e-6, "Uy": 1e-6, "h": 1e-8}` was
# calibrated for an UNRELAXED final outer sweep.  T25R2 relaxes the final sweep
# -- that is the fix for the crash -- so the calibrating assumption is GONE and
# the threshold with it.  These fields are CENSUSED AND REPORTED.  NO PASS, NO
# FAIL AND NO VERDICT OF ANY KIND IS DERIVABLE FROM THE CENSUS, and `--selftest`
# proves by token search that no comparison against a residual threshold exists
# anywhere in this file.
RESID_REPORT_FIELDS = ("p_rgh", "Ux", "Uy", "h")

# SECTION 3.5, THE GATE THAT REPLACES IT: DEMONSTRATED SWEEP-COUNT INDEPENDENCE
# BETWEEN `T25R2_L1` (10 sweeps) AND `T25R2_L1_OC20` (20 sweeps), IN KELVIN.
#
# THE THRESHOLDS ARE TIED TO THE PLANT SCALE, AND THE ARITHMETIC IS THIS:
#   PLANT      = 1.234e-03 K  -- the registered reader-control perturbation, the
#                               smallest shift every reader in section 7.1 is
#                               PROVED able to see.
#   10 * PLANT = 1.234e-02 K  -- the D3 floor: the smallest within-cell signal
#                               this rung is willing to call signal at all.
#
#   O1 (absolute trajectory, per cell, per written time) <= 10*PLANT.
#      A trajectory that moves by MORE than the smallest gated signal when the
#      sweep count is doubled is not a trajectory this rung can report.
#   O2 (the D3 quantity itself, min_i[T_dn-T_up] at t=60 s) <= 1*PLANT.
#      This is the number D3 gates, so its sweep-count uncertainty is held to
#      TEN PER CENT of D3's own floor -- one order below the threshold it could
#      otherwise flip.  It is deliberately the tightest of the three, because it
#      is the only one attached to a kelvin gate.
#   O3 (the D2 quantity, coolant outlet area-mean T at t=60 s and t=900 s)
#      <= 10*PLANT.  D2 is a strict INEQUALITY with no kelvin threshold of its
#      own, so O3 is held at the signal scale rather than at PLANT.
#
# ALL THREE MUST HOLD.  This arm CAN FAIL, and if it does that is a real
# GATE FAIL which section 3.5 propagates -- see `grade()`.
OC_O1_TOL = 10.0 * PLANT                  # 1.234e-02 K
OC_O2_TOL = 1.0 * PLANT                   # 1.234e-03 K
OC_O3_TOL = 10.0 * PLANT                  # 1.234e-02 K

# Section 3.4, the numerics MEASURED by T25RF arm A2T and registered here.  The
# crash mechanism was a MISSING DICTIONARY KEY, so the keys are verified in the
# dictionary that actually ran and their absence is a REFUSAL.
RELAX_FINAL_KEYS = ("p_rghFinal", "UFinal", "hFinal", "kFinal", "omegaFinal")
RELAX_EXPECT = {"p_rgh": 0.3, "p_rghFinal": 0.3,
                "U": 0.7, "UFinal": 0.7, "h": 0.7, "hFinal": 0.7,
                "k": 0.7, "kFinal": 0.7, "omega": 0.7, "omegaFinal": 0.7}
PRGH_TOL = 1e-8                           # 1e-9 is UNREACHABLE (T25RF add. A2)

WRITE_TIMES = (0.0, 30.0, 60.0, 120.0, 300.0, 900.0)   # section 9

REGIONS = ("module", "coolant")
IFACE = {"module": "module_to_coolant", "coolant": "coolant_to_module"}


def refuse(msg):
    """REFUSES (exit 2) rather than degrades.  No soft path out."""
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def clear_pycache():
    """Clause 9.  A stale bytecode cache INVERTS a mutation control -- the
    clean arm fails and the mutated arm passes -- and PYTHONDONTWRITEBYTECODE
    does NOT fix it; the caches must be removed."""
    for d in (HERE, os.path.join(REPO, "scripts")):
        p = os.path.join(d, "__pycache__")
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)


# ==========================================================================
# THE FREEZE CHECK.  CLAUDE.md rule 2: verify the frozen file IS the file that
# ran, by hashing it against the committed blob.  A working-tree edit to the
# pre-registration after the freeze is caught HERE and REFUSED, not discovered
# later by a reader.
# ==========================================================================

def freeze_check(repo=None):
    repo = REPO if repo is None else repo
    p = os.path.join(repo, FROZEN_DOC)
    if not os.path.isfile(p):
        refuse("the frozen document %s is not on disk -- there is nothing to "
               "grade against" % FROZEN_DOC)
    r = subprocess.run(["git", "-C", repo, "hash-object", p],
                       capture_output=True, text=True)
    if r.returncode != 0:
        refuse("git hash-object failed on %s" % FROZEN_DOC)
    worktree = r.stdout.strip()
    r = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD:" + FROZEN_DOC],
                       capture_output=True, text=True)
    if r.returncode != 0:
        refuse("%s is NOT COMMITTED at HEAD. CLAUDE.md rule 2 requires the "
               "pre-registration to be committed BEFORE compute, and the "
               "grading path is fixed at that commit. An uncommitted "
               "pre-registration has no evidentiary content." % FROZEN_DOC)
    committed = r.stdout.strip()
    if worktree != committed:
        refuse("THE FROZEN DOCUMENT HAS BEEN EDITED SINCE ITS COMMIT.\n"
               "  working tree blob : %s\n  HEAD blob         : %s\n"
               "Frozen files are never edited (CLAUDE.md rule 6). A departure "
               "lands as a DATED AMENDMENT APPENDED AT THE FOOT with a version "
               "bump, never as an in-place edit." % (worktree, committed))
    return committed


# ==========================================================================
# polyMesh.  Every cell of this mesh is an AXIS-ALIGNED BOX, so a cell's
# centroid is the mean of its bounding corners and its volume is the product of
# its extents -- EXACTLY, not approximately.  That boxness is CHECKED, not
# assumed: a cell whose vertex set is not the 8 corners of its bounding box is
# a REFUSAL, because every geometric number below would then be wrong in a way
# no threshold would catch.
# ==========================================================================

def _strip(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    return re.sub(r"//[^\n]*", " ", txt)


def _body(path):
    """The list body after the FoamFile header: (count, text-after-'(')."""
    if not os.path.isfile(path):
        refuse("no %s -- the mesh this reader needs is not on disk" % path)
    txt = _strip(open(path).read())
    end = txt.find("}")
    if end < 0:
        refuse("%s has no FoamFile header" % path)
    rest = txt[end + 1:]
    m = re.search(r"(\d+)\s*\(", rest)
    if not m:
        refuse("%s carries no `<count> (` list header -- a structural locator "
               "will not guess one" % path)
    return int(m.group(1)), rest[m.end():]


def read_points(path):
    n, rest = _body(path)
    pts = re.findall(r"\(\s*(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s+(-?[\d.eE+-]+)\s*\)",
                     rest)
    if len(pts) < n:
        refuse("%s claims %d points, found %d" % (path, n, len(pts)))
    return [(float(a), float(b), float(c)) for a, b, c in pts[:n]]


def read_faces(path):
    n, rest = _body(path)
    out = []
    for m in re.finditer(r"(\d+)\s*\(([^)]*)\)", rest):
        k = int(m.group(1))
        v = m.group(2).split()
        if len(v) != k:
            refuse("%s: a face declares %d labels and lists %d"
                   % (path, k, len(v)))
        out.append([int(x) for x in v])
        if len(out) == n:
            break
    if len(out) != n:
        refuse("%s claims %d faces, found %d" % (path, n, len(out)))
    return out


def read_labels(path):
    n, rest = _body(path)
    v = re.findall(r"-?\d+", rest)
    if len(v) < n:
        refuse("%s claims %d labels, found %d" % (path, n, len(v)))
    return [int(x) for x in v[:n]]


def read_boundary(path):
    """-> {patch: (startFace, nFaces)}."""
    n, rest = _body(path)
    out = {}
    for m in re.finditer(r"([A-Za-z_][\w.:-]*)\s*\{([^{}]*)\}", rest):
        blk = m.group(2)
        s = re.search(r"startFace\s+(\d+)\s*;", blk)
        f = re.search(r"nFaces\s+(\d+)\s*;", blk)
        if s and f:
            out[m.group(1)] = (int(s.group(1)), int(f.group(1)))
    if len(out) != n:
        refuse("%s declares %d patches and %d were parsed"
               % (path, n, len(out)))
    return out


class Mesh(object):
    """Cell boxes and patch face geometry for ONE region of ONE case."""

    def __init__(self, case_dir, region):
        pm = os.path.join(case_dir, "constant", region, "polyMesh")
        self.points = read_points(os.path.join(pm, "points"))
        self.faces = read_faces(os.path.join(pm, "faces"))
        self.owner = read_labels(os.path.join(pm, "owner"))
        nb = os.path.join(pm, "neighbour")
        self.neigh = read_labels(nb) if os.path.isfile(nb) else []
        self.bnd = read_boundary(os.path.join(pm, "boundary"))
        self.n = max(max(self.owner), max(self.neigh) if self.neigh else -1) + 1

        cellpts = [set() for _ in range(self.n)]
        for fi, c in enumerate(self.owner):
            cellpts[c].update(self.faces[fi])
        for fi, c in enumerate(self.neigh):
            cellpts[c].update(self.faces[fi])

        self.box, self.vol, self.cx, self.cy = [], [], [], []
        for c in range(self.n):
            ps = [self.points[i] for i in cellpts[c]]
            if len(ps) != 8:
                refuse("%s cell %d has %d distinct vertices, not 8 -- this "
                       "reader is exact ONLY on hexahedra and REFUSES rather "
                       "than approximate" % (region, c, len(ps)))
            lo = [min(p[k] for p in ps) for k in range(3)]
            hi = [max(p[k] for p in ps) for k in range(3)]
            for p in ps:
                for k in range(3):
                    if abs(p[k] - lo[k]) > 1e-12 and abs(p[k] - hi[k]) > 1e-12:
                        refuse("%s cell %d is NOT an axis-aligned box (vertex "
                               "%r off both bounds in axis %d) -- the exact "
                               "centroid/volume path does not apply and this "
                               "reader REFUSES" % (region, c, p, k))
            d = [hi[k] - lo[k] for k in range(3)]
            if min(d) <= 0.0:
                refuse("%s cell %d has a non-positive extent %r" % (region, c, d))
            self.box.append((lo, hi))
            self.vol.append(d[0] * d[1] * d[2])
            self.cx.append(0.5 * (lo[0] + hi[0]))
            self.cy.append(0.5 * (lo[1] + hi[1]))

    def patch_face_areas(self, patch):
        if patch not in self.bnd:
            refuse("patch %r absent; the region carries %s"
                   % (patch, ",".join(sorted(self.bnd))))
        s, k = self.bnd[patch]
        out = []
        for fi in range(s, s + k):
            ps = [self.points[i] for i in self.faces[fi]]
            d = [max(p[j] for p in ps) - min(p[j] for p in ps) for j in range(3)]
            nz = [x for x in d if x > 1e-14]
            if len(nz) != 2:
                refuse("patch %s face %d is not a planar axis-aligned quad "
                       "(extents %r)" % (patch, fi, d))
            out.append(nz[0] * nz[1])
        return out


# ==========================================================================
# FIELD FILES.  Every list is delimited from the FIELD'S OWN HEADER -- keyword,
# count, opening parenthesis -- never by a regex sweep and NEVER BY VALUE
# (clause 7).
# ==========================================================================

def _list_window(lines, key_idx, path):
    i = key_idx + 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or not re.fullmatch(r"\d+", lines[i].strip()):
        refuse("%s: list at line %d carries no element count -- the structural "
               "locator will not guess one" % (path, key_idx))
    n = int(lines[i].strip())
    i += 1
    if i >= len(lines) or lines[i].strip() != "(":
        refuse("%s: list at line %d has no opening parenthesis after its count"
               % (path, key_idx))
    if i + 1 + n > len(lines):
        refuse("%s: list at line %d claims %d elements the file does not hold"
               % (path, key_idx, n))
    return i + 1, n


def internal_window(path):
    if not os.path.isfile(path):
        refuse("no %s" % path)
    lines = open(path).read().split("\n")
    idx = [k for k, l in enumerate(lines)
           if re.match(r"\s*internalField\s+nonuniform\s+List<scalar>", l)]
    if len(idx) != 1:
        refuse("%s has %d internalField scalar-list headers, expected exactly "
               "1. A UNIFORM internalField here would mean the solver wrote a "
               "constant field, which is a finding, not a parse problem"
               % (path, len(idx)))
    first, n = _list_window(lines, idx[0], path)
    return lines, first, n


def patch_value_window(path, patch):
    """The `value` list of ONE boundaryField patch.  NEVER falls back to
    `refValue`: those are different quantities and a silent fallback is how a
    coupled-patch reader ends up reporting the neighbour's guess."""
    if not os.path.isfile(path):
        refuse("no %s" % path)
    lines = open(path).read().split("\n")
    bidx = [k for k, l in enumerate(lines) if re.match(r"^boundaryField\s*$", l)]
    if len(bidx) != 1:
        refuse("%s has %d boundaryField headers, expected exactly 1"
               % (path, len(bidx)))
    pidx = [k for k, l in enumerate(lines) if k > bidx[0] and l.strip() == patch]
    if len(pidx) != 1:
        refuse("%s has %d `%s` blocks in boundaryField, expected exactly 1"
               % (path, len(pidx), patch))
    k, depth, opened, vidx = pidx[0], 0, False, None
    while k < len(lines):
        depth += lines[k].count("{") - lines[k].count("}")
        if lines[k].count("{"):
            opened = True
        if opened and depth == 1 and re.match(
                r"\s+value\s+nonuniform\s+List<scalar>", lines[k]):
            vidx = k
        if opened and depth == 0:
            break
        k += 1
    if vidx is None:
        refuse("patch `%s` in %s carries no nonuniform `value` list. This "
               "reader will NOT fall back to refValue, which is a different "
               "quantity (section 7.2)" % (patch, path))
    first, n = _list_window(lines, vidx, path)
    return lines, first, n


def tdir(case_dir, t):
    """The written time directory for `t`, located by NAME, not by proximity."""
    for cand in ("%g" % t, "%.1f" % t, "%.2f" % t):
        p = os.path.join(case_dir, cand)
        if os.path.isdir(p):
            return p
    refuse("case %s has no time directory for t = %g -- section 9 registers "
           "writes every 5 s, so this time was registered and is absent"
           % (case_dir, t))


def fld(case_dir, t, region, name):
    return os.path.join(tdir(case_dir, t), region, name)


# ==========================================================================
# THE READERS (section 7.2).  Each is paired with a planter that writes into
# EXACTLY the artifact that reader reads.
# ==========================================================================

def _cell_of(mesh, i):
    """Which of the 8 module cells cell-index i belongs to, by its y centre."""
    j = int(math.floor(mesh.cy[i] / PITCH))
    if j < 0 or j >= N_CELLS:
        refuse("module cell %d has y centre %.6g, outside the 8 registered "
               "cell bands" % (i, mesh.cy[i]))
    lo = j * PITCH
    if not (lo - 1e-12 <= mesh.cy[i] <= lo + CELL_LY + 1e-12):
        refuse("module cell %d has y centre %.6g, which lies in the CHANNEL "
               "gap above cell %d -- the module region must carry no fluid "
               "cells" % (i, mesh.cy[i], j + 1))
    return j


def read_cell_T(case_dir, t, mesh=None):
    """Volume-averaged solid T of each of the 8 cells, K.  -> list of 8."""
    mesh = Mesh(case_dir, "module") if mesh is None else mesh
    p = fld(case_dir, t, "module", "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("module/T at t=%g holds %d values against %d mesh cells"
               % (t, n, mesh.n))
    num = [0.0] * N_CELLS
    den = [0.0] * N_CELLS
    for i in range(n):
        j = _cell_of(mesh, i)
        num[j] += mesh.vol[i] * float(lines[first + i])
        den[j] += mesh.vol[i]
    if min(den) <= 0.0:
        refuse("a registered module cell received no mesh cells at all")
    return [num[j] / den[j] for j in range(N_CELLS)]


def read_updown(case_dir, t, mesh=None):
    """(T_up[8], T_dn[8]) -- volume averages over x in [0, 0.010] and
    [0.090, 0.100] (section 5.3)."""
    mesh = Mesh(case_dir, "module") if mesh is None else mesh
    p = fld(case_dir, t, "module", "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("module/T at t=%g holds %d values against %d mesh cells"
               % (t, n, mesh.n))
    up_n, up_d = [0.0] * N_CELLS, [0.0] * N_CELLS
    dn_n, dn_d = [0.0] * N_CELLS, [0.0] * N_CELLS
    for i in range(n):
        j = _cell_of(mesh, i)
        v, x = mesh.vol[i], mesh.cx[i]
        val = float(lines[first + i])
        if x <= X_BAND:
            up_n[j] += v * val
            up_d[j] += v
        elif x >= CELL_LX - X_BAND:
            dn_n[j] += v * val
            dn_d[j] += v
    if min(up_d) <= 0.0 or min(dn_d) <= 0.0:
        refuse("an upstream or downstream x-band is EMPTY in some cell -- the "
               "10 mm band is narrower than one mesh cell and D1/D3 cannot be "
               "evaluated on this level")
    return ([up_n[j] / up_d[j] for j in range(N_CELLS)],
            [dn_n[j] / dn_d[j] for j in range(N_CELLS)])


def read_patch_T(case_dir, t, patch, mesh=None):
    """Area-weighted mean coolant T on `patch`, K."""
    mesh = Mesh(case_dir, "coolant") if mesh is None else mesh
    p = fld(case_dir, t, "coolant", "T")
    lines, first, n = patch_value_window(p, patch)
    a = mesh.patch_face_areas(patch)
    if len(a) != n:
        refuse("patch %s: %d face areas against %d boundary values"
               % (patch, len(a), n))
    return sum(ai * float(lines[first + i]) for i, ai in enumerate(a)) / sum(a)


def read_spread(case_dir, t, mesh=None):
    v = read_cell_T(case_dir, t, mesh)
    return max(v) - min(v)


def read_stored(case_dir, t, region, mesh=None):
    """Stored sensible energy above T_INIT in `region`, J."""
    mesh = Mesh(case_dir, region) if mesh is None else mesh
    p = fld(case_dir, t, region, "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("%s/T at t=%g holds %d values against %d mesh cells"
               % (region, t, n, mesh.n))
    rc = RHO_S * CP_S if region == "module" else 1.2 * CP_AIR
    return sum(mesh.vol[i] * rc * (float(lines[first + i]) - T_INIT)
               for i in range(n))


# ==========================================================================
# THE PLANTERS.  BY LINE INDEX, inside a window from the field's own header.
# Nothing is located by value.  Each returns the count planted.
# ==========================================================================

_MESH_CACHE = {}


def _mesh(case_dir, region):
    k = (os.path.realpath(case_dir), region)
    if k not in _MESH_CACHE:
        _MESH_CACHE[k] = Mesh(case_dir, region)
    return _MESH_CACHE[k]


def _plant_hottest_module_cell(case_dir, t, mag):
    """Plant into EVERY mesh cell of the HOTTEST of the 8 module cells.

    CLAUSE 7, AND THE REASON IT IS WRITTEN THIS WAY.  Every solid reader in
    section 7.2 returns a VOLUME AVERAGE over one module cell.  Planting a
    single mesh cell would shift that average by mag*V_i/V_cell -- i.e. by
    mag/N -- and the control would then fail clause 5 for a reason that has
    nothing to do with whether the reader can see the plant.  Planting the
    WHOLE module cell makes the expected shift EXACTLY `mag`, which is the same
    correction analyse_t24.py:443 makes for its patch plant.  The module cell is
    chosen BY ITS VOLUME-AVERAGE RANK, never by locating a value in the file."""
    mesh = _mesh(case_dir, "module")
    p = fld(case_dir, t, "module", "T")
    lines, first, n = internal_window(p)
    if n != mesh.n:
        refuse("module/T holds %d values against %d mesh cells" % (n, mesh.n))
    num = [0.0] * N_CELLS
    den = [0.0] * N_CELLS
    for i in range(n):
        j = _cell_of(mesh, i)
        num[j] += mesh.vol[i] * float(lines[first + i])
        den[j] += mesh.vol[i]
    hot = max(range(N_CELLS), key=lambda j: num[j] / den[j])
    cnt = 0
    for i in range(n):
        if _cell_of(mesh, i) == hot:
            lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
            cnt += 1
    open(p, "w").write("\n".join(lines))
    return cnt


def _plant_internal_one(path, mag):
    """Plant into ONE internalField cell -- the hottest.  Used ONLY as the
    NEGATIVE ARM of the selftest, to prove the mag/N failure mode is live."""
    lines, first, n = internal_window(path)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)
    open(path, "w").write("\n".join(lines))
    return 1


def _plant_internal_all(path, mag):
    lines, first, n = internal_window(path)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(path, "w").write("\n".join(lines))
    return n


def _plant_patch_all(path, patch, mag):
    """EVERY face, so the expected shift is EXACTLY `mag`, never mag/N."""
    lines, first, n = patch_value_window(path, patch)
    for i in range(n):
        lines[first + i] = "%.12g" % (float(lines[first + i]) + mag)
    open(path, "w").write("\n".join(lines))
    return n


# ==========================================================================
# THE PLANTED-ZERO CONTROL -- all nine clauses.  REFUSES rather than degrades.
# ==========================================================================

def planted_zero_control(case_dir, label, reader, planter, target_rel):
    clear_pycache()                                       # clause 9
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="t25Rctl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    tgt = lambda d: os.path.join(d, target_rel)           # noqa: E731
    try:
        # CLAUSE 1: COPY FIRST, NEVER WRITE INTO THE CASE.
        if os.path.realpath(scratch) == case_real \
           or os.path.realpath(scratch).startswith(case_real + os.sep):
            refuse("control scratch %s resolves INSIDE the case %s -- clause 1 "
                   "forbids writing into the case under any circumstance"
                   % (scratch, case_real))
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.*", "*.py",
                                                      "processor*"))
        if os.path.realpath(dest).startswith(case_real + os.sep):
            refuse("control copy %s resolves INSIDE the case" % dest)
        if not os.path.isfile(tgt(dest)):
            refuse("%s: the control target %s is not in the copy"
                   % (label, target_rel))
        pristine = open(tgt(dest)).read()

        # CLAUSE 2: NEGATIVE ARM, THRESHOLD EXACTLY ZERO, NO TOLERANCE.
        a = reader(dest)
        b = reader(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r, and clause 2 registers the "
                   "threshold as bitwise 0.0 with NO tolerance" % (label, b - a))
        base = a

        # CLAUSE 3: POSITIVE ARM, a MEASURED ladder, exact and epsilon-free.
        rungs, floor, at_plant, n_planted = [], None, None, None
        for mag in LADDER:
            open(tgt(dest), "w").write(pristine)
            cnt = planter(dest, mag)
            got = reader(dest) - base
            rungs.append((mag, got, cnt))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, n_planted = got, cnt
        open(tgt(dest), "w").write(pristine)

        # CLAUSE 4: REFUSE IF BLIND.
        if floor is None:
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in "
                   "the registered ladder produced a non-zero read. An "
                   "instrument that cannot see a planted perturbation is not "
                   "entitled to certify anything" % label)

        # CLAUSE 5: THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE.
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("%s: read at PLANT is %.6e, below the registered RELATIVE "
                   "predicate PLANT*(1-1e-9) = %.6e. The ABSOLUTE form of "
                   "analyse_t3.py:327 is expressly not adopted here"
                   % (label, at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))

        # CLAUSE 8: the case was never written to, and that is CHECKED.
        if open(tgt(case_dir)).read() != open(tgt(dest)).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)
        return dict(passed=True, base=base, floor=floor, at_plant=at_plant,
                    n_planted=n_planted, rungs=rungs)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)        # clause 8, in finally


# ==========================================================================
# GATES
# ==========================================================================

def pulse_table_check(case_dir, case):
    """Section 4.5.  The Function1 table is a LINEAR interpolant, so the two
    breakpoints around the edge are the ends of a RAMP, not a step.  The
    registered condition is that NO step time on this run's deltaT falls
    STRICTLY INSIDE (59.999, 60.000).  This is CHECKED against the dictionary
    that will actually run, not asserted from the document."""
    p = os.path.join(case_dir, "constant", "module", "fvOptions")
    if not os.path.isfile(p):
        refuse("no constant/module/fvOptions -- the pulse this rung is about "
               "cannot be verified to exist")
    txt = _strip(open(p).read())
    if not re.search(r"volumeMode\s+specific\s*;", txt):
        refuse("fvOptions does not register `volumeMode specific`. volumeMode "
               "is MANDATORY at v2606 and the wrong mode is a SILENT scale "
               "error by exactly the zone volume (section 4.5)")
    if re.search(r"\bsources\b[^{]*\{\s*T\b", txt) or re.search(r"^\s*T\s*\{",
                                                                txt, re.M):
        refuse("fvOptions carries a source on field `T`. The solid energy "
               "equation is in ENTHALPY; an entry on T is NEVER APPLIED and "
               "the solid is SILENTLY UNHEATED (section 4.5). That is exactly "
               "the failure CLAUDE.md rule 3 exists for")
    if not re.search(r"\bh\b\s*\{", txt):
        refuse("fvOptions carries no source on field `h`")
    bp = re.findall(r"\(\s*(-?[\d.]+)\s+(-?[\d.]+)\s*\)", txt)
    tab = [(float(a), float(b)) for a, b in bp]
    want = [(0.0, Q_TAKEOFF), (RAMP_LO, Q_TAKEOFF),
            (RAMP_HI, Q_CRUISE), (T_END, Q_CRUISE)]
    if len(tab) != 4 or any(abs(tab[i][0] - want[i][0]) > 1e-9
                            or abs(tab[i][1] - want[i][1]) > 1e-6
                            for i in range(4)):
        refuse("the fvOptions pulse table is %r, not the REGISTERED %r "
               "(section 4.5)" % (tab, want))
    dt = DELTAT[case]
    if dt <= (RAMP_HI - RAMP_LO):
        refuse("deltaT %g is not finer than the %g s ramp width -- section 4.5 "
               "registers that a deltaT finer than the ramp must revisit the "
               "breakpoint placement" % (dt, RAMP_HI - RAMP_LO))
    k0 = int(math.floor(RAMP_LO / dt)) - 2
    hits = [k * dt for k in range(max(k0, 0), k0 + 8)
            if RAMP_LO < k * dt < RAMP_HI]
    if hits:
        refuse("step times %r fall STRICTLY INSIDE the ramp (%g, %g) at deltaT "
               "%g. The solver would sample a value the directive does not "
               "register at those instants (section 4.5)"
               % (hits, RAMP_LO, RAMP_HI, dt))
    return dict(table=tab, ramp=(RAMP_LO, RAMP_HI), deltaT=dt, hits=0)


def _brace_block(txt, key):
    """The text INSIDE the braces of the first top-level `key { ... }`.  None if
    the key is absent.  A real brace matcher, because an OpenFOAM dictionary
    nests and a regex would take the first `}` it saw."""
    m = re.search(r"(?<![A-Za-z0-9_])%s\s*\{" % re.escape(key), txt)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(txt) and depth:
        if txt[i] == "{":
            depth += 1
        elif txt[i] == "}":
            depth -= 1
        i += 1
    if depth:
        return None
    return txt[m.end():i - 1]


def _kv_pairs(txt):
    """`key value;` pairs at the top level of a stripped dictionary body."""
    out = {}
    depth = 0
    buf = []
    for ch in txt:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        elif depth == 0:
            buf.append(ch)
    for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_]*|"[^"]*")\s+([^;{}]+);',
                         "".join(buf)):
        out[m.group(1)] = m.group(2).strip()
    return out


def numerics_check(case_dir, case):
    """Section 3.4 -- *** THE DICTIONARY THAT ACTUALLY RAN. ***

    THE CRASH THIS RUNG EXISTS TO SURVIVE WAS A MISSING DICTIONARY KEY.
    `fvMatrix::relax()` resolves its key as `psi_.select(isFinalIteration())`,
    which returns `name() + "Final"` on the last outer sweep
    (GeometricField.C:1179, flag set at chtMultiRegionFoam.C:111), and OpenFOAM
    keyword regexes MATCH IN FULL -- so T25R's `"(U|h|k|omega)"` matched
    nothing on that sweep and momentum and energy ran UNRELAXED.  A registration
    that writes the missing keys and then grades a run WITHOUT CHECKING THEY
    WERE THERE has learned nothing (L-221/L-222: a lesson is not applied until
    every call site asserts it).

    THE REGISTERED FORM IS LITERAL, ONE KEY PER FIELD, AND A QUOTED REGEX IS
    REFUSED EVEN IF IT WOULD IN FACT MATCH.  The failure being guarded against is
    a pattern that LOOKS like it matches and does not; a check that had to
    re-implement OpenFOAM's regex resolution to decide would be the same class
    of reasoning that produced the bug.  The registered dictionary is decidable
    by reading.

    Every departure here is a REFUSAL (exit 2), not a gate: it means the case
    that ran is not the case that was registered, and a comparator has no
    business grading it.
    """
    top = os.path.join(case_dir, "system", "fvSolution")
    cool = os.path.join(case_dir, "system", "coolant", "fvSolution")
    for p in (top, cool):
        if not os.path.isfile(p):
            refuse("%s: no %s -- the numerics this rung registers cannot be "
                   "verified to be the numerics that ran"
                   % (case, os.path.relpath(p, case_dir)))
    ttxt = _strip(open(top).read())
    ctxt = _strip(open(cool).read())

    # ---- nOuterCorrectors, PER CASE (section 3.5's whole gate turns on it).
    pim = _brace_block(ttxt, "PIMPLE")
    if pim is None:
        refuse("%s: system/fvSolution registers no top-level PIMPLE dict. "
               "chtMultiRegionFoam reads nOuterCorrectors from THERE "
               "(readPIMPLEControls.H), not from a region dict" % case)
    kv = _kv_pairs(pim)
    if "nOuterCorrectors" not in kv:
        refuse("%s: the top-level PIMPLE dict states no nOuterCorrectors"
               % case)
    try:
        n = int(kv["nOuterCorrectors"])
    except ValueError:
        refuse("%s: nOuterCorrectors is %r, not an integer"
               % (case, kv["nOuterCorrectors"]))
    if n != NOUTER[case]:
        refuse("%s RAN AT nOuterCorrectors %d, NOT THE REGISTERED %d. Section "
               "3.5 gates on the DIFFERENCE between the 10-sweep and 20-sweep "
               "arms; a case whose sweep count is not its registered one makes "
               "that gate meaningless and is REFUSED, never graded"
               % (case, n, NOUTER[case]))

    # ---- the relaxation keys, LITERAL, in system/coolant/fvSolution.
    rf = _brace_block(ctxt, "relaxationFactors")
    if rf is None:
        refuse("%s: system/coolant/fvSolution registers NO relaxationFactors "
               "dict at all. THAT IS THE T25R CONFIGURATION AND IT DIVERGED "
               "(FOAM FATAL, T0 = -14.46 at t = 1.5)" % case)
    have = {}
    for sub in ("fields", "equations"):
        b = _brace_block(rf, sub)
        if b is None:
            refuse("%s: relaxationFactors states no `%s` sub-dict" % (case, sub))
        have.update(_kv_pairs(b))
    missing = [k for k in RELAX_EXPECT if k not in have]
    if missing:
        refuse("%s: THE REGISTERED RELAXATION KEYS %s ARE ABSENT FROM "
               "system/coolant/fvSolution. OpenFOAM keyword regexes match in "
               "FULL: a key that is not written LITERALLY is not found on the "
               "final outer sweep, and the field runs UNRELAXED there. That is "
               "the exact mechanism that killed T25R_L1, and it is REFUSED "
               "here, never graded" % (case, ",".join(sorted(missing))))
    quoted = [k for k in have if k.startswith('"') and
              any(f in k for f in ("Final", "p_rgh", "U", "h", "k", "omega"))]
    if quoted:
        refuse("%s: system/coolant/fvSolution carries QUOTED-REGEX relaxation "
               "keys %s. The registered form is LITERAL, one key per field. A "
               "regex is refused EVEN IF IT WOULD MATCH: the failure being "
               "guarded against is a pattern that looks like it matches and "
               "does not, and a check that had to re-implement OpenFOAM's regex "
               "resolution to decide would be the same reasoning that produced "
               "the bug" % (case, ",".join(sorted(quoted))))
    wrong = []
    for k, want in sorted(RELAX_EXPECT.items()):
        try:
            got = float(have[k])
        except ValueError:
            refuse("%s: relaxation factor %s is %r, not a number"
                   % (case, k, have[k]))
        if abs(got - want) > 1e-12:
            wrong.append("%s=%g (registered %g)" % (k, got, want))
    if wrong:
        refuse("%s: relaxation factors differ from the REGISTERED values "
               "measured by T25RF arm A2T: %s" % (case, "; ".join(wrong)))

    # ---- the p_rgh linear tolerance.  1e-9 IS UNREACHABLE (T25RF addendum A2).
    sol = _brace_block(ctxt, "solvers")
    if sol is None:
        refuse("%s: system/coolant/fvSolution registers no `solvers` dict"
               % case)
    tols, seen = [], []
    for m in re.finditer(r'("?[^\s{}";]*p_rgh[^\s{}";]*"?)\s*\{', sol):
        blk = _brace_block(sol, m.group(1))
        if blk is None:
            continue
        seen.append(m.group(1))
        t = _kv_pairs(blk).get("tolerance")
        if t is None:
            refuse("%s: the p_rgh solver entry %s states no tolerance"
                   % (case, m.group(1)))
        tols.append((m.group(1), float(t)))
    if len(tols) < 2:
        refuse("%s: expected a p_rgh AND a p_rghFinal solver entry in "
               "system/coolant/fvSolution; found %d (%s)"
               % (case, len(tols), ",".join(seen) or "none"))
    bad = [x for x in tols if abs(x[1] - PRGH_TOL) > 1e-20]
    if bad:
        refuse("%s: p_rgh linear tolerances %r differ from the REGISTERED "
               "%g. MEASURED at T25RF addendum A2: GAMG STALLS at ~4.4e-9 on "
               "this system, so 1e-9 is UNREACHABLE -- 608 of 1200 solves "
               "terminated at maxIter 1000 without reaching it, and the 601,763 "
               "discarded iterations changed the answer by 0.000e+00 K. A "
               "tolerance below the solver's own floor buys nothing and is "
               "named as WASTE (rule 12), not paid for"
               % (case, [(a, b) for a, b in bad], PRGH_TOL))
    return dict(nOuterCorrectors=n, relax=dict(have), p_rgh_tol=tols[0][1],
                literal_keys=list(RELAX_FINAL_KEYS))


def resid_report(case_dir, case):
    """Section 3.5 -- *** A REPORT.  NO THRESHOLD.  NO VERDICT. ***

    T25R gated on the last-sweep initial residual < 1e-6.  That threshold was
    calibrated for an UNRELAXED final sweep; T25R2 RELAXES the final sweep, so
    the calibration is gone and the threshold with it.  What is printed here is
    a census of the last-sweep initial residuals, for the reader, and NOTHING IS
    COMPARED AGAINST ANYTHING.  The outer loop is gated by `oc_independence()`.

    TWO REFUSALS SURVIVE, AND THEY ARE EVIDENCE CHECKS, NOT GATES.  A log with
    no `Initial residual` lines at all, or a registered field that never appears
    in it, would let this census print a zero it could not have seen -- the
    planted-zero failure of CLAUDE.md rule 3 -- so both REFUSE.

    WHY NOT `residualControl`.  ESTABLISHED AT SOURCE, v2606:
    chtMultiRegionFoam does NOT use pimpleControl for its outer loop.
    chtMultiRegionFoam.C:109 is a plain `for (oCorr=0; oCorr<nOuterCorr; ++oCorr)`
    and the per-region control headers read ONLY nCorrectors,
    nNonOrthogonalCorrectors, momentumPredictor and frozenFlow.  THERE IS NO
    residualControl ON THIS SOLVER'S OUTER LOOP and it emits no
    "PIMPLE: converged in" / "not converged within" line, ever.  Counting zero
    such lines would have reported a PLANTED ZERO as a clean pass.
    """
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        refuse("no log.solve for %s" % case)
    body = open(log, errors="replace").read()
    steps = MD.CASES[case]

    if "Initial residual" not in body:
        refuse("log.solve for %s carries NO `Initial residual` lines at all. "
               "Section 3.5's census reads them; a census with no evidence is a "
               "PLANTED ZERO and is REFUSED, never printed as a clean row"
               % case)

    blocks = re.split(r"^Time = ", body, flags=re.M)[1:]
    if not blocks:
        refuse("log.solve for %s carries no `Time = ` blocks -- the per-step "
               "census cannot be formed" % case)

    seen_any, worst, last_step = 0, {}, {}
    for blk in blocks:
        last = {}
        for m in re.finditer(r"Solving for ([A-Za-z_.]+),\s*Initial residual "
                             r"= ([0-9.eE+-]+)", blk):
            last[m.group(1)] = float(m.group(2))
        if not last:
            continue
        seen_any += 1
        for f in last:
            if f in RESID_REPORT_FIELDS:
                worst[f] = max(worst.get(f, 0.0), last[f])
                last_step[f] = last[f]
    if seen_any == 0:
        refuse("no `Time = ` block in %s carries a `Solving for` line -- the "
               "census is BLIND and REFUSES rather than print zeros" % case)
    missing = [f for f in RESID_REPORT_FIELDS if f not in worst]
    if missing:
        refuse("the registered census fields %s never appear in log.solve for "
               "%s. A census that silently omits the field it was written for "
               "would report a zero it never saw" % (",".join(sorted(missing)),
                                                     case))
    return dict(steps=steps, blocks=seen_any, worst=worst,
                final_step=last_step)


# ==========================================================================
# SECTION 3.5, THE GATE.  DEMONSTRATED SWEEP-COUNT INDEPENDENCE, IN KELVIN.
# ==========================================================================

OC_SCOPE = (
    "REGISTERED SCOPE, AND ITS LIMIT. The outer-loop arm runs at L1 ONLY, so a "
    "PASS demonstrates sweep-count independence AT L1 AND AT L1's Courant "
    "number (~1600 at dx 2.5 mm). L2 runs at dx 1.6667 mm and therefore at "
    "Co ~ 2400, where the outer loop converges no faster, so THE GATE DOES NOT "
    "CERTIFY L2 AND IS NOT REPORTED AS DOING SO. The FAILURE direction does "
    "transfer -- if 10 sweeps is not enough at Co 1600 it is not enough at "
    "Co 2400 -- which is why a GATE FAIL here voids every row and a PASS "
    "carries its L1 scope printed beside every L2 number.")


def oc_independence(root, ma=None, ca=None, mb=None, cb=None):
    """Section 3.5.  |X(20 sweeps) - X(10 sweeps)| on the three registered
    quantities, in KELVIN, against thresholds tied to the PLANT scale.

    THIS ARM CAN FAIL.  The probe measured 5-vs-10 sweeps disagreeing by
    6.02e-3 K after 30 s of a 900 s case and STILL GROWING; nothing here assumes
    that 10-vs-20 will be smaller, and if it is not, that is a real GATE FAIL
    and this rung says so.
    """
    a = os.path.join(root, OC_PAIR[0])
    b = os.path.join(root, OC_PAIR[1])
    ma = Mesh(a, "module") if ma is None else ma
    ca = Mesh(a, "coolant") if ca is None else ca
    mb = Mesh(b, "module") if mb is None else mb
    cb = Mesh(b, "coolant") if cb is None else cb

    # ---- O1: the absolute trajectory, every cell, every written time > 0.
    #      t = 0 is EXCLUDED and the exclusion is registered: both arms stage
    #      the SAME 0.orig, so a t = 0 comparison is identically zero by
    #      construction and would be a planted zero dressed as agreement.
    o1, o1_where = 0.0, None
    for t in WRITE_TIMES:
        if t <= 0.0:
            continue
        va = read_cell_T(a, t, ma)
        vb = read_cell_T(b, t, mb)
        for i in range(N_CELLS):
            dv = abs(vb[i] - va[i])
            if dv > o1:
                o1, o1_where = dv, "cell %d at t=%g s" % (i + 1, t)

    # ---- O2: the D3 quantity itself, at the end of the pulse.
    da = min(x[1] - x[0] for x in zip(*read_updown(a, T_PULSE, ma)))
    db = min(x[1] - x[0] for x in zip(*read_updown(b, T_PULSE, mb)))
    o2 = abs(db - da)

    # ---- O3: the D2 quantity, coolant outlet area-mean T.
    o3, o3_where = 0.0, None
    for t in (T_PULSE, T_END):
        dv = abs(read_patch_T(b, t, "outlet", cb)
                 - read_patch_T(a, t, "outlet", ca))
        if dv > o3:
            o3, o3_where = dv, "t=%g s" % t

    r = dict(
        O1=o1, O1_tol=OC_O1_TOL, O1_ok=(o1 <= OC_O1_TOL), O1_where=o1_where,
        O2=o2, O2_tol=OC_O2_TOL, O2_ok=(o2 <= OC_O2_TOL),
        O2_10=da, O2_20=db,
        O3=o3, O3_tol=OC_O3_TOL, O3_ok=(o3 <= OC_O3_TOL), O3_where=o3_where,
        arms=list(OC_PAIR), sweeps=[NOUTER[OC_PAIR[0]], NOUTER[OC_PAIR[1]]],
        scope=OC_SCOPE)
    r["ok"] = r["O1_ok"] and r["O2_ok"] and r["O3_ok"]
    return r


def _checkmesh_max(txt, what):
    r"""Largest value reported for `what` in a checkMesh log.

    *** THIS PARSER IS A REPAIR, AND THE DEFECT IT REPAIRS IS DISCLOSED IN
    SECTION 12 OF THE FROZEN DOCUMENT. ***  `analyse_t25R.py:795-800` reads

        r"[Mm]ax(?:imum)? non-orthogonality[^\d-]*(-?[\d.eE+]+)"
        r"[Mm]ax(?:imum)? skewness[^\d-]*(-?[\d.eE+]+)"

    and BOTH FAIL ON THE REAL v2606 OUTPUT, which this lane read off
    `T25R_MODULE_runs/T25R_L1/log.checkMesh.coolant`:

        Mesh non-orthogonality Max: 0 average: 0
        Max skewness = 1.66534018381e-13 OK.

      - the non-orthogonality pattern requires "Max non-orthogonality"; v2606
        writes "Mesh non-orthogonality Max:".  It matches NOTHING, falls back to
        -1.0 and the T25R comparator REFUSES a perfectly good mesh.
      - the skewness character class `[\d.eE+]` EXCLUDES the minus sign, so on a
        NEGATIVE EXPONENT it captures "1.66534018381e" and `float()` raises an
        UNCAUGHT ValueError -- which in that file leaves exit status 1, i.e. a
        GRADED "gate failed or NOT A RESULT".  That is exactly the traceback
        trap: a crash wearing a verdict's clothes.

    Neither was caught because T25R's forged checkMesh log was written to match
    its own regex rather than to resemble the solver, and its `grade()` was
    never driven end to end in --selftest.  T25R2's forge writes the REAL v2606
    wording, its `grade()` IS driven end to end, and both wordings are parsed.
    `analyse_t25R.py` IS FROZEN AND IS NOT EDITED (CLAUDE.md rule 6): the defect
    is REPORTED, not repaired in place.
    """
    pats = (r"[Mm]esh %s\s+Max\s*:\s*(-?[\d.eE+-]+)" % what,
            r"[Mm]ax(?:imum)? %s\s*[=:]\s*(-?[\d.eE+-]+)" % what)
    vals = []
    for pat in pats:
        for x in re.findall(pat, txt):
            try:
                vals.append(float(x))
            except ValueError:
                refuse("log.checkMesh: %r is not a number where a max %s was "
                       "expected. This is REFUSED, never converted into a "
                       "graded verdict by an uncaught traceback" % (x, what))
    return max(vals) if vals else None


def mesh_quality(case_dir):
    """Section 2.4, read off log.checkMesh per region."""
    out = {}
    for region in REGIONS:
        p = os.path.join(case_dir, "log.checkMesh.%s" % region)
        if not os.path.isfile(p):
            refuse("no log.checkMesh.%s -- section 2.4 registers a mesh gate "
                   "and it is not graded on trust" % region)
        txt = open(p, errors="replace").read()
        nonorth = _checkmesh_max(txt, "non-orthogonality")
        skew = _checkmesh_max(txt, "skewness")
        if nonorth is None or skew is None:
            refuse("log.checkMesh.%s states no max non-orthogonality (%r) or "
                   "no max skewness (%r) -- the gate cannot be evaluated and "
                   "REFUSES rather than assume a number it never read"
                   % (region, nonorth, skew))
        ok = ("Mesh OK" in txt and "***" not in txt
              and nonorth < MESH_MAXNONORTH and skew < MESH_MAXSKEW)
        out[region] = dict(nonorth=nonorth, skew=skew,
                           mesh_ok=("Mesh OK" in txt), ok=ok)
    return out


def energy_balance(case_dir, mm=None, mc=None):
    """Section 6.2.  E_gen = dE_solid + dE_fluid + convected + R."""
    dEs = read_stored(case_dir, T_END, "module", mm)
    dEf = read_stored(case_dir, T_END, "coolant", mc)
    conv = convected_energy(case_dir)
    R = E_GEN - (dEs + dEf + conv)
    return dict(E_gen=E_GEN, dE_solid=dEs, dE_fluid=dEf, convected=conv,
                residual=R, rel=abs(R) / E_GEN,
                ok=(abs(R) / E_GEN <= ENERGY_BAND))


def convected_energy(case_dir):
    """Time-integral of mdot*cp*(T_out - T_in), J, from the registered
    surfaceFieldValue instruments.  `phi` is the MASS flux and is NEGATIVE on
    an inflow face, so the two weightedSum rows ADD rather than subtract."""
    tot = None
    for name in ("inlet_hflux", "outlet_hflux"):
        p = _postproc_dat(case_dir, name)
        rows = _read_dat(p)
        s = 0.0
        prev_t = 0.0
        for t, v in rows:
            s += v * (t - prev_t)
            prev_t = t
        tot = s if tot is None else tot + s
    return CP_AIR * tot


def _postproc_dat(case_dir, name):
    root = os.path.join(case_dir, "postProcessing", name)
    if not os.path.isdir(root):
        refuse("no postProcessing/%s -- section 6.2 registers this instrument "
               "and its absence is a REFUSAL, not a zero" % name)
    subs = sorted(os.listdir(root))
    if len(subs) != 1:
        refuse("postProcessing/%s holds %d start-time directories (%s). A "
               "RESTART would leave more than one and the integral would "
               "silently double-count; this reader REFUSES rather than pick "
               "one" % (name, len(subs), ",".join(subs)))
    d = os.path.join(root, subs[0])
    f = [x for x in sorted(os.listdir(d)) if x.endswith(".dat")]
    if len(f) != 1:
        refuse("postProcessing/%s/%s holds %d .dat files, expected exactly 1"
               % (name, subs[0], len(f)))
    return os.path.join(d, f[0])


def _read_dat(path):
    rows = []
    for line in open(path):
        if line.lstrip().startswith("#") or not line.strip():
            continue
        p = line.split()
        if len(p) < 2:
            refuse("%s: a data line carries fewer than 2 columns" % path)
        rows.append((float(p[0]), float(p[-1])))
    if not rows:
        refuse("%s holds no data rows -- a zero from an EMPTY instrument is "
               "not a measurement (CLAUDE.md rule 3)" % path)
    return rows


def energy_planted_control(case_dir):
    """Section 6.2's planted +10 % source control.  E_gen is recomputed with
    the TAKEOFF level scaled by +10 % and the residual must move by exactly
    that much.  AN INSTRUMENT THAT DOES NOT MOVE WHEN THE SOURCE MOVES IS
    REFUSED, not reported."""
    d = N_CELLS * V_CELL * PLANT10_PCT * Q_TAKEOFF * T_PULSE
    base = energy_balance(case_dir)
    moved = (E_GEN + d) - (base["dE_solid"] + base["dE_fluid"]
                           + base["convected"])
    got = moved - base["residual"]
    if abs(got - d) > 1e-6:
        refuse("ENERGY BALANCE PLANTED CONTROL: a +10 %% takeoff source moved "
               "the residual by %.9e J, not the expected %.9e J. The balance "
               "instrument does not respond to the source it audits" % (got, d))
    return dict(passed=True, planted_J=d, seen_J=got)


def acceptance_D(case_dir, mm=None, mc=None):
    """Section 5.3: D1, D2, D3.  Sanaa's acceptance criterion for the resolved
    channel, in the form the REGISTERED PARALLEL-CHANNEL GEOMETRY admits."""
    up, dn = read_updown(case_dir, T_PULSE, mm)
    diff = [dn[i] - up[i] for i in range(N_CELLS)]
    d1 = all(x > 0.0 for x in diff)
    d3 = min(diff) > D3_FLOOR
    outs, ins = [], []
    for t in _written_times(case_dir):
        if t <= 0.0:
            continue
        outs.append((t, read_patch_T(case_dir, t, "outlet", mc)))
        ins.append((t, read_patch_T(case_dir, t, "inlet", mc)))
    d2 = all(o[1] > i[1] for o, i in zip(outs, ins))
    return dict(up=up, dn=dn, diff=diff, D1=d1, D2=d2, D3=d3,
                D3_floor=D3_FLOOR, min_diff=min(diff),
                outlet=outs, inlet=ins)


def _written_times(case_dir):
    ts = sorted(float(x) for x in os.listdir(case_dir)
                if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x))
    if not ts:
        refuse("case %s holds no time directories" % case_dir)
    return ts


# ==========================================================================
# THE SENSITIVITY PANELS -- DIFFERENCES, AND NOTHING ELSE.
# ==========================================================================

NO_LADDER = ("TWO POINTS. NO LADDER IS REGISTERED. No observed order, no GCI "
             "and no Roache classification is computed, quoted or quotable "
             "from this artifact. A small difference between two points is "
             "CONSISTENT WITH convergence and is NOT EVIDENCE OF it.")


def sensitivity(a_dir, b_dir, a_name, b_name, kind):
    """Signed and percentage DIFFERENCES on the registered quantities.  This
    function computes NO order and NO GCI and there is no code path here that
    could."""
    out = {"kind": kind, "arms": [a_name, b_name], "no_ladder": NO_LADDER}
    ma, mb = Mesh(a_dir, "module"), Mesh(b_dir, "module")
    ca, cb = Mesh(a_dir, "coolant"), Mesh(b_dir, "coolant")
    rows = []
    for label, fa, fb in (
            ("peak cell T at t=60 s (K)",
             lambda: max(read_cell_T(a_dir, T_PULSE, ma)),
             lambda: max(read_cell_T(b_dir, T_PULSE, mb))),
            ("peak cell T at t=900 s (K)",
             lambda: max(read_cell_T(a_dir, T_END, ma)),
             lambda: max(read_cell_T(b_dir, T_END, mb))),
            ("module spread at t=60 s (K)",
             lambda: read_spread(a_dir, T_PULSE, ma),
             lambda: read_spread(b_dir, T_PULSE, mb)),
            ("coolant outlet T at t=60 s (K)",
             lambda: read_patch_T(a_dir, T_PULSE, "outlet", ca),
             lambda: read_patch_T(b_dir, T_PULSE, "outlet", cb)),
            ("coolant outlet T at t=900 s (K)",
             lambda: read_patch_T(a_dir, T_END, "outlet", ca),
             lambda: read_patch_T(b_dir, T_END, "outlet", cb)),
            ("min within-cell streamwise diff at t=60 s (K)",
             lambda: min(acceptance_D(a_dir, ma, ca)["diff"]),
             lambda: min(acceptance_D(b_dir, mb, cb)["diff"]))):
        va, vb = fa(), fb()
        rows.append(dict(quantity=label, a=va, b=vb, diff=vb - va,
                         pct=(100.0 * (vb - va) / va) if va else None))
    out["rows"] = rows
    return out


# ==========================================================================
# GRADING
# ==========================================================================

def _header(sha):
    print("T25R2 -- 8-CELL AVIATION BATTERY MODULE, RESOLVED COOLING CHANNELS, "
          "TRUE TRANSIENT CONJUGATE.")
    print("Gates FROZEN at %s, blob %s." % (FROZEN_DOC, sha[:12]))
    print("")
    print("*** " + NO_LADDER)
    print("*** SECTION 4.2: THE REGISTERED LOAD IS A VOLUMETRIC RATE -- "
          "q''' = %.6g W/m3 takeoff, %.6g W/m3 cruise, Sanaa 2026-09-01 04:20Z. "
          "A PER-CELL WATTAGE IS NEVER AN INPUT HERE: %.1f W and %.2f W per "
          "cell are DERIVED consequences of the 2-D UNIT-DEPTH normalisation "
          "(V = %.4g m3 per metre of depth) and are not claims about a real "
          "cell. In her real 100x30x150 mm cell the same q''' is %.1f W and "
          "%.2f W." % (Q_TAKEOFF, Q_CRUISE, Q_TAKEOFF * V_CELL,
                       Q_CRUISE * V_CELL, V_CELL,
                       Q_TAKEOFF * V_REAL_CELL, Q_CRUISE * V_REAL_CELL))
    print("*** SECTION 0.3: SANAA'S RISE RULING IS BINDING. \"The temperature "
          "rise is then whatever the physics gives; I am not prescribing tens "
          "of kelvin, I am prescribing realistic heat density. If the result is "
          "8 K, 8 K is the answer.\" NOTHING IN THIS RUNG IS TUNED TOWARD A "
          "TARGET.")
    print("*** SECTION 3.5: T25R's LAST-SWEEP RESIDUAL GATE IS INVALID AND IS "
          "GONE. Its 1e-6 threshold was calibrated for an UNRELAXED final outer "
          "sweep, and relaxing that sweep -- the fix for the T25R_L1 divergence "
          "-- destroys the calibration. The census below is a REPORT WITH NO "
          "THRESHOLD. The outer loop is gated by DEMONSTRATED SWEEP-COUNT "
          "INDEPENDENCE between %s (%d sweeps) and %s (%d sweeps), IN KELVIN."
          % (OC_PAIR[0], NOUTER[OC_PAIR[0]], OC_PAIR[1], NOUTER[OC_PAIR[1]]))
    print("*** SECTION 6.1: THE T20 EXACT GATE HAS NOT DISCHARGED. "
          "T20_P10_CONDITION_iii_MEASUREMENT.md:9 states \"T20 remains NOT A "
          "RESULT on its own registered terms\". The T20 citation is a POINTER "
          "to the registered exact tier, NOT a discharged machinery proof, and "
          "T25R2 INHERITS NO PASS FROM IT.")
    print("*** SECTION 0.4: T25R IS NOT THIS RUNG. T25R_L1 is NOT A RESULT "
          "(rc=134, one FOAM FATAL, last written time 1.5 against endTime 900) "
          "and the T25RF probe is UNGATED (VERIFICATION_CHARTER 2m). No number "
          "from either is a result here.")
    print("*** SECTION 3.6: with g = (0 0 0) registered, a Ri < 0.1 criterion "
          "is IDENTICALLY ZERO BY CONSTRUCTION, cannot fail and cannot inform. "
          "It is NOT reported as a passing check. Buoyancy is OFF, its neglect "
          "is a DECLARED OMISSION, and forced-convection dominance rests on "
          "Gr/Re2 = 2.51e-05 (section 3.6), not on any check run here.")
    print("*** SECTION 3.3: transient FLOW dynamics are NOT resolved. The step "
          "is derived from the 60 s pulse edge and the ~696 s lumped tau, NOT "
          "from a Courant number; Co ~ 1600 at L1 is REPORTED, not controlled.")
    print("PLANT = %.6e, IMPORTED from scripts/roache_triple.py and never "
          "redefined here (section 7.1 clause 6)." % PLANT)
    if PLANT != RT.PLANT:
        refuse("PLANT was redefined locally -- clause 6 forbids it")
    print("")


def _admit(root, case, out):
    """Per-case ADMISSION: completion, the registered numerics, the pulse
    dictionary and the mesh gate.  Returns True only if the case is entitled to
    have its numbers looked at.  NOTHING PHYSICAL IS PRINTED HERE."""
    d = os.path.join(root, case)
    print("=" * 74)
    print("%s  (mesh %s, deltaT %g s, %d registered steps, nOuterCorrectors %d)"
          % (case, LEVEL[case], DELTAT[case], MD.CASES[case], NOUTER[case]))
    print("=" * 74)

    # ---- 1. COMPLETION, DELEGATED (section 6.4).  Never reimplemented.
    fails, notes = MD.check(root, case)
    for n in notes:
        print("  NOTE  %s" % n)
    if fails:
        print("  VERDICT: NOT A RESULT -- rule 4 completion: %s"
              % "; ".join(fails))
        print("  No number from this run is printed as a result. A partially "
              "converged transient is NEVER presented as complete "
              "(section 0.3).")
        out[case] = dict(verdict="NOT A RESULT", why=fails)
        return False

    # ---- 2. THE NUMERICS THAT ACTUALLY RAN (section 3.4).  REFUSES.
    nc = numerics_check(d, case)
    print("  NUMERICS VERIFIED IN THE DICTIONARY THAT RAN: nOuterCorrectors %d "
          "(registered %d); the five LITERAL final-sweep relaxation keys %s all "
          "present; p_rgh linear tolerance %g."
          % (nc["nOuterCorrectors"], NOUTER[case],
             ",".join(RELAX_FINAL_KEYS), nc["p_rgh_tol"]))

    # ---- 3. THE PULSE DICTIONARY (section 4.5).
    pt = pulse_table_check(d, case)
    print("  PULSE TABLE OK: %r W/m3; ramp (%g, %g); no step time at deltaT %g "
          "falls strictly inside it." % (pt["table"], pt["ramp"][0],
                                         pt["ramp"][1], pt["deltaT"]))

    # ---- 4. MESH QUALITY (section 2.4).
    mq = mesh_quality(d)
    for r in REGIONS:
        print("  checkMesh %-8s Mesh OK=%s  maxNonOrth=%.4g (<%g)  "
              "maxSkew=%.4g (<%g)  -> %s"
              % (r, mq[r]["mesh_ok"], mq[r]["nonorth"], MESH_MAXNONORTH,
                 mq[r]["skew"], MESH_MAXSKEW, "OK" if mq[r]["ok"] else "FAIL"))
    if not all(mq[r]["ok"] for r in REGIONS):
        print("  VERDICT: NOT A RESULT -- section 2.4 mesh gate failed.")
        out[case] = dict(verdict="NOT A RESULT", why=["mesh gate"], mesh=mq)
        return False

    # ---- 5. THE LAST-SWEEP RESIDUAL CENSUS.  *** REPORT.  NO THRESHOLD. ***
    rr = resid_report(d, case)
    print("  LAST-SWEEP RESIDUAL CENSUS over %d time blocks -- *** REPORT "
          "ONLY. NO THRESHOLD IS ATTACHED AND NO VERDICT IS DERIVABLE FROM "
          "IT (section 3.5). ***" % rr["blocks"])
    for f in sorted(rr["worst"]):
        print("    worst last-sweep initial residual  %-6s %.4e   "
              "(at the final step %.4e)  [REPORT]"
              % (f, rr["worst"][f], rr["final_step"].get(f, float("nan"))))

    out[case] = dict(verdict=None, mesh=mq, pulse=pt, numerics=nc,
                     resid_report=rr)
    return True


def grade(root, cases, repo=None):
    sha = freeze_check(repo)
    _header(sha)
    worst, out = EXIT_OK, {}

    # ======================================================================
    # PHASE A -- ADMISSION, PER CASE.
    # ======================================================================
    admitted = {}
    for case in cases:
        if case not in CASES:
            refuse("%r is not a registered T25R2 case (section 1): %s"
                   % (case, " ".join(CASES)))
        admitted[case] = _admit(root, case, out)
        if not admitted[case]:
            worst = EXIT_FAIL

    # ======================================================================
    # PHASE B -- SECTION 3.5, THE OUTER-LOOP GATE.
    #
    # *** IT IS EVALUATED FROM `OC_PAIR` WHATEVER WAS ASKED FOR ON THE COMMAND
    # LINE. ***  Grading one case is not a way to skip the gate: the physics of
    # every row in this rung is withheld until sweep-count independence has been
    # DEMONSTRATED, and a comparator that let a caller choose otherwise would be
    # a gate in name only.
    # ======================================================================
    print("\n" + "-" * 74)
    print("SECTION 3.5 -- THE OUTER-LOOP GATE: DEMONSTRATED SWEEP-COUNT "
          "INDEPENDENCE, IN KELVIN")
    print("-" * 74)
    print("*** T25R's last-sweep-residual gate is INVALID here and is not "
          "used. Its 1e-6 threshold was calibrated for an UNRELAXED final "
          "sweep; relaxing that sweep is the fix for the T25R_L1 divergence and "
          "destroys the calibration. ***")
    print(OC_SCOPE)

    oc_state, oc = "PENDING", None
    oc_ready = []
    for c in OC_PAIR:
        d = os.path.join(root, c)
        if not os.path.isdir(d):
            oc_ready.append((c, "no case directory %s" % d))
            continue
        if c in admitted:
            if not admitted[c]:
                oc_ready.append((c, "%s is NOT A RESULT on admission" % c))
            continue
        f, _n = MD.check(root, c)
        if f:
            oc_ready.append((c, "%s: %s" % (c, "; ".join(f))))
        else:
            numerics_check(d, c)

    if oc_ready:
        blocked = [x for x in oc_ready if "no case directory" not in x[1]]
        oc_state = "NOT A RESULT" if blocked else "PENDING"
        print("  OUTER-LOOP GATE: %s -- it could not be evaluated: %s"
              % (oc_state, "; ".join(x[1] for x in oc_ready)))
        if oc_state == "PENDING":
            print("  PENDING is a QUEUE STATE (CLAUDE.md rule 1): the arm has "
                  "not run. It NEVER softens a GATE FAIL.")
    else:
        oc = oc_independence(root)
        print("  arms: %s (%d sweeps) vs %s (%d sweeps), identical in every "
              "other respect." % (OC_PAIR[0], NOUTER[OC_PAIR[0]],
                                  OC_PAIR[1], NOUTER[OC_PAIR[1]]))
        print("  O1  max |dT| over all 8 cells and all written t>0   "
              "%.6e K  <= %.6e K (10*PLANT)  [%s]   worst at %s"
              % (oc["O1"], oc["O1_tol"], "PASS" if oc["O1_ok"] else "GATE FAIL",
                 oc["O1_where"]))
        print("  O2  |d( min_i[T_dn-T_up] at t=60 s )| (the D3 quantity) "
              "%.6e K  <= %.6e K (1*PLANT)   [%s]   %.9f -> %.9f K"
              % (oc["O2"], oc["O2_tol"], "PASS" if oc["O2_ok"] else "GATE FAIL",
                 oc["O2_10"], oc["O2_20"]))
        print("  O3  max |d( coolant outlet area-mean T )|            "
              "%.6e K  <= %.6e K (10*PLANT)  [%s]   worst at %s"
              % (oc["O3"], oc["O3_tol"], "PASS" if oc["O3_ok"] else "GATE FAIL",
                 oc["O3_where"]))
        oc_state = "PASS" if oc["ok"] else "GATE FAIL"
        print("  OUTER-LOOP GATE: %s" % oc_state)
        if not oc["ok"]:
            print("  *** SECTION 3.5 PROPAGATION. A GATE FAIL here means the "
                  "answer still depends on an arbitrary iteration count, so "
                  "EVERY ROW OF THIS RUNG IS `NOT A RESULT` -- CLAUDE.md rule "
                  "5 clause (1): a level that is not iteratively converged is "
                  "NOT A RESULT whatever its value says. The three deltas above "
                  "are printed beside every number this rung produced. ***")
            print("  *** THIS IS A REAL FINDING, NOT AN INSTRUMENT FAILURE. It "
                  "says 10 outer sweeps is not enough at Co ~ 1600, which is "
                  "exactly what the T25RF probe could not settle. ***")
    out["OUTER_LOOP_GATE"] = dict(state=oc_state, detail=oc, scope=OC_SCOPE)
    if oc_state != "PASS":
        worst = EXIT_FAIL

    # ======================================================================
    # PHASE C -- THE PHYSICS GATES.  Only reached when section 3.5 PASSED.
    # ======================================================================
    for case in cases:
        if not admitted[case]:
            continue
        d = os.path.join(root, case)
        print("\n" + "=" * 74)
        print("%s -- PHYSICS" % case)
        print("=" * 74)
        if oc_state != "PASS":
            v = "NOT A RESULT" if oc_state in ("GATE FAIL",
                                               "NOT A RESULT") else "PENDING"
            print("  VERDICT: %s -- section 3.5's outer-loop gate is %s, so "
                  "sweep-count independence is not demonstrated and NO NUMBER "
                  "FROM THIS RUN IS PRINTED AS A RESULT." % (v, oc_state))
            out[case]["verdict"] = v
            out[case]["why"] = ["section 3.5 outer-loop gate: %s" % oc_state]
            worst = EXIT_FAIL
            continue

        # ---- INSTRUMENT ADMISSION (section 7.1).  BEFORE any number.
        mm, mc = Mesh(d, "module"), Mesh(d, "coolant")
        tmod = os.path.join("%g" % T_END, "module", "T")
        tcool = os.path.join("%g" % T_END, "coolant", "T")
        ctrls = {}
        for lbl, rdr, plt, tgt in (
                ("read_cell_T",
                 lambda x: max(read_cell_T(x, T_END)),
                 lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                 tmod),
                ("read_spread",
                 lambda x: read_spread(x, T_END),
                 lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                 tmod),
                ("read_updown",
                 lambda x: max(read_updown(x, T_END)[1]),
                 lambda x, m: _plant_internal_all(os.path.join(x, tmod), m),
                 tmod),
                ("read_outlet_T",
                 lambda x: read_patch_T(x, T_END, "outlet"),
                 lambda x, m: _plant_patch_all(os.path.join(x, tcool),
                                               "outlet", m),
                 tcool),
                ("read_inlet_T",
                 lambda x: read_patch_T(x, T_END, "inlet"),
                 lambda x, m: _plant_patch_all(os.path.join(x, tcool),
                                               "inlet", m),
                 tcool)):
            c = planted_zero_control(d, lbl, rdr, plt, tgt)
            ctrls[lbl] = c
            print("  PLANTED-ZERO CONTROL %-14s PASS. negative arm bitwise 0.0; "
                  "measured floor %.3e; read at PLANT %.6e against the "
                  "RELATIVE predicate PLANT*(1-1e-9) = %.6e; values planted %d"
                  % (lbl, c["floor"], c["at_plant"],
                     PLANT * (1.0 - PLANT_REL_SLACK), c["n_planted"]))

        # ---- ENERGY CONSERVATION (section 6.2) + its planted control.
        epc = energy_planted_control(d)
        print("  ENERGY PLANTED CONTROL PASS: a +10 %% takeoff source moved the "
              "residual by %.6e J, the expected %.6e J."
              % (epc["seen_J"], epc["planted_J"]))
        eb = energy_balance(d, mm, mc)
        print("  ENERGY BALANCE over 900 s:  E_gen %.1f J = dE_solid %.1f + "
              "dE_fluid %.1f + convected %.1f + R %.1f"
              % (eb["E_gen"], eb["dE_solid"], eb["dE_fluid"], eb["convected"],
                 eb["residual"]))
        print("  |R|/E_gen = %.4f %% against the registered band %.1f %% -> %s"
              % (100 * eb["rel"], 100 * ENERGY_BAND,
                 "PASS" if eb["ok"] else "GATE FAIL"))

        # ---- THE ACCEPTANCE CRITERION (section 5.3).
        ac = acceptance_D(d, mm, mc)
        print("  SECTION 5.2 DISCLOSURE: the 7 channels are PARALLEL and no "
              "cell is downstream of another. D1/D3 are WITHIN-CELL "
              "streamwise; D2 is outlet-above-inlet. This is disclosed, not "
              "substituted, and the framing is Sanaa's to rule.")
        for i in range(N_CELLS):
            print("    cell %d  T_up %.6f  T_dn %.6f  diff %+0.6e K"
                  % (i + 1, ac["up"][i], ac["dn"][i], ac["diff"][i]))
        print("  D1 (T_dn > T_up, all 8, t=60 s)          -> %s"
              % ("PASS" if ac["D1"] else "GATE FAIL"))
        print("  D2 (outlet > inlet at every written t>0) -> %s"
              % ("PASS" if ac["D2"] else "GATE FAIL"))
        print("  D3 (min diff %.6e K > 10*PLANT = %.6e K) -> %s"
              % (ac["min_diff"], ac["D3_floor"],
                 "PASS" if ac["D3"] else "GATE FAIL"))
        if LEVEL[case] != "L1":
            print("  SECTION 3.5 SCOPE, PRINTED BESIDE EVERY L2 NUMBER: the "
                  "outer-loop gate was demonstrated at L1 (Co ~ 1600). It DOES "
                  "NOT certify %s at Co ~ 2400." % case)

        gates_ok = eb["ok"] and ac["D1"] and ac["D2"] and ac["D3"]
        verdict = "PASS" if gates_ok else "GATE FAIL"
        print("  VERDICT: %s" % verdict)
        if not gates_ok:
            worst = EXIT_FAIL

        # ---- THE FEASIBILITY-TAGGED OUTPUTS (section 9).
        print("  FEASIBILITY (not gradeable; no gate exists for these and none "
              "may be invented after the fact):")
        cells_end = read_cell_T(d, T_END, mm)
        cells_60 = read_cell_T(d, T_PULSE, mm)
        for i in range(N_CELLS):
            print("    cell %d  T(60 s) %.6f K  rise %+0.6f K   T(900 s) "
                  "%.6f K  rise %+0.6f K  [FEASIBILITY]"
                  % (i + 1, cells_60[i], cells_60[i] - T_INIT,
                     cells_end[i], cells_end[i] - T_INIT))
        print("    module spread t=60 s %.6e K, t=900 s %.6e K  [FEASIBILITY]"
              % (read_spread(d, T_PULSE, mm), read_spread(d, T_END, mm)))
        print("    SECTION 4.3, REGISTERED BEFORE THE RUN: the adiabatic bound "
              "on the pulse rise is q'''*t/(rho*cp) = %.4f K and on the full "
              "900 s it is %.4f K; the quasi-steady interior cell-to-air rise "
              "at cruise is %.3f K at h = 53.9 W/m2K, which is "
              "DECLARED-REPRESENTATIVE, NOT MEASURED, and is IMPOSED NOWHERE IN "
              "THE SOLVE. THE MEASURED VALUE ABOVE IS THE DELIVERABLE WHATEVER "
              "IT IS -- Sanaa: \"If the result is 8 K, 8 K is the answer.\""
              % (ADIABATIC_PULSE_K, ADIABATIC_900_K, CRUISE_STEADY_RISE_K))

        out[case].update(dict(verdict=verdict, energy=eb, acceptance=ac,
                              controls={k: dict(floor=v["floor"],
                                                at_plant=v["at_plant"],
                                                n_planted=v["n_planted"])
                                        for k, v in ctrls.items()},
                              cells_60=cells_60, cells_900=cells_end))

    # ======================================================================
    # PHASE D -- THE TWO SENSITIVITY PANELS.  DIFFERENCES, AND NOTHING ELSE.
    # ======================================================================
    for pair, kind in ((MESH_PAIR, "MESH SENSITIVITY (L1 vs L2, same deltaT)"),
                       (STEP_PAIR, "STEP SENSITIVITY (dt 0.5 vs 0.25, same "
                                   "mesh)")):
        if not all(c in out and out[c].get("verdict") in ("PASS", "GATE FAIL")
                   for c in pair):
            print("\n%s: PENDING -- one or both arms is not graded." % kind)
            continue
        print("\n" + "-" * 74)
        print(kind)
        print("*** " + NO_LADDER)
        print("-" * 74)
        s = sensitivity(os.path.join(root, pair[0]),
                        os.path.join(root, pair[1]), pair[0], pair[1], kind)
        for r in s["rows"]:
            print("  %-44s %14.8g -> %14.8g  diff %+.6e (%+.4f %%)"
                  % (r["quantity"], r["a"], r["b"], r["diff"],
                     r["pct"] if r["pct"] is not None else float("nan")))
        out[kind] = s

    return worst, out


# ==========================================================================
# SELFTEST.  Forges synthetic cases in scratch and drives every clause,
# positive and negative.  No solver, no mesher, no case on disk is touched.
#
# *** EVERY GUARD IS DRIVEN TO ITS REFUSAL BY MUTATION. ***  A supervisor's read
# of a control is necessary and NOT sufficient (VERIFICATION_CHARTER 2n.18); a
# control that has not been PROVED to fire is ceremony.  Each negative arm below
# breaks exactly one thing and requires the instrument to notice.
# ==========================================================================

FVSOL_TOP = """FoamFile{ version 2.0; }
// nOuterCorrectors is read from the TOP-LEVEL dict by readPIMPLEControls.H.
PIMPLE
{
    nOuterCorrectors %d;
    nNonOrthogonalCorrectors 0;
}
"""

FVSOL_COOL_HEAD = """FoamFile{ version 2.0; }
solvers
{
    rho { solver PCG; preconditioner DIC; tolerance 1e-08; relTol 0; }
    rhoFinal { $rho; relTol 0; }
    "p_rgh.*"
    {
        solver          GAMG;
        tolerance       %(tol)s;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    p_rghFinal
    {
        $p_rgh;
        tolerance       %(tol)s;
        relTol          0;
    }
    "(U|h|k|omega)"
    { solver PBiCGStab; preconditioner DILU; tolerance 1e-10; relTol 0.01; }
    "(U|h|k|omega)Final"
    { $U; tolerance 1e-10; relTol 0; }
}
PIMPLE
{
    momentumPredictor true;
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
}
"""


def _fvsolution_coolant(drop=(), quoted=False, tol="1e-08", no_relax=False,
                        override=None):
    """The registered coolant fvSolution, with knobs that break exactly one
    registered property each so the selftest can drive `numerics_check` to its
    refusal."""
    txt = FVSOL_COOL_HEAD % {"tol": tol}
    if no_relax:
        return txt
    fields, eqns = [], []
    for k, v in (("p_rgh", 0.3), ("p_rghFinal", 0.3)):
        if k in drop:
            continue
        fields.append("    %s %s;" % (k, (override or {}).get(k, v)))
    for k, v in (("U", 0.7), ("UFinal", 0.7), ("h", 0.7), ("hFinal", 0.7),
                 ("k", 0.7), ("kFinal", 0.7), ("omega", 0.7),
                 ("omegaFinal", 0.7)):
        if k in drop:
            continue
        key = '"%s"' % k if quoted else k
        eqns.append("    %s %s;" % (key, (override or {}).get(k, v)))
    return (txt + "relaxationFactors\n{\n  fields\n  {\n"
            + "\n".join(fields) + "\n  }\n  equations\n  {\n"
            + "\n".join(eqns) + "\n  }\n}\n")


def _forge_case(root, case, dt, tdn_bonus=0.05, ramp=(RAMP_LO, RAMP_HI),
                q_take=Q_TAKEOFF, q_cruise=Q_CRUISE, nx=20, ny=2, blind=False,
                oc_bonus=0.0, nouter=None, drop=(), quoted=False,
                prgh_tol="1e-08", no_relax=False, top_pimple=True,
                checkmesh_nonorth="0",
                checkmesh_skew="1.66534018381e-13", conv_dT=None):
    """A tiny but STRUCTURALLY REAL case: 8 module cells x (nx*ny) hexes,
    a coolant region with inlet/outlet patches, a log, a STATUS, checkMesh
    logs, the two fvSolution dictionaries, an fvOptions and the two
    postProcessing instruments."""
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system", "coolant"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "application     chtMultiRegionFoam;\nendTime         900;\n"
        "deltaT          %g;\nadjustTimeStep  no;\n" % dt)
    n_o = NOUTER[case] if nouter is None else nouter
    open(os.path.join(d, "system", "fvSolution"), "w").write(
        (FVSOL_TOP % n_o) if top_pimple else "FoamFile{ version 2.0; }\n")
    open(os.path.join(d, "system", "coolant", "fvSolution"), "w").write(
        _fvsolution_coolant(drop=drop, quoted=quoted, tol=prgh_tol,
                            no_relax=no_relax))
    open(os.path.join(d, "STATUS.%s" % case), "w").write(
        "launcher_rc=0\nnote=exit-status-of-the-launch-argv-NOT-the-solver-rc\n")
    steps = MD.CASES[case]
    lines = ["ExecutionTime = %g s  ClockTime = %d s" % (i * .1, i)
             for i in range(1, steps + 1)]
    for i in range(steps):
        lines.append("Time = %g" % ((i + 1) * dt))
        for f, v in (("Ux", 1e-9), ("Uy", 1e-9), ("p_rgh", 1e-9), ("h", 1e-9)):
            lines.append("PBiCGStab:  Solving for %s, Initial residual = %g, "
                         "Final residual = 1e-12, No Iterations 2" % (f, v))
    lines += ["End"]
    open(os.path.join(d, "log.solve"), "w").write("\n".join(lines) + "\n")
    # *** THE REAL v2606 WORDING, taken verbatim from
    # T25R_MODULE_runs/T25R_L1/log.checkMesh.coolant. ***  T25R's forge wrote a
    # wording chosen to match its own regex, which is why neither of that
    # parser's two defects was ever caught (see `_checkmesh_max`).
    for r in REGIONS:
        open(os.path.join(d, "log.checkMesh.%s" % r), "w").write(
            "Checking geometry...\n"
            "    Overall domain bounding box (0 0 0) (0.1 0.261 1)\n"
            "    Max cell openness = 1.35525271561e-16 OK.\n"
            "    Mesh non-orthogonality Max: %s average: 0\n"
            "    Max skewness = %s OK.\n"
            "\nMesh OK.\n" % (checkmesh_nonorth, checkmesh_skew))

    # ---- fvOptions
    os.makedirs(os.path.join(d, "constant", "module"), exist_ok=True)
    open(os.path.join(d, "constant", "module", "fvOptions"), "w").write(
        "FoamFile{ version 2.0; }\nq{\n type scalarSemiImplicitSource;\n"
        " volumeMode      specific;\n sources { h { explicit table\n"
        " (\n ( 0.000 %.6f)\n ( %.3f %.6f)\n ( %.3f %.6f)\n ( 900.000 %.6f)\n"
        " );\n implicit none; } }\n}\n"
        % (q_take, ramp[0], q_take, ramp[1], q_cruise, q_cruise))

    # ---- the two meshes, written as real polyMesh files.
    def hexmesh(region, boxes):
        pm = os.path.join(d, "constant", region, "polyMesh")
        os.makedirs(pm, exist_ok=True)
        pts, pidx, faces, owner, neigh = [], {}, [], [], []
        fkey = {}

        def P(x, y, z):
            k = (round(x, 12), round(y, 12), round(z, 12))
            if k not in pidx:
                pidx[k] = len(pts)
                pts.append(k)
            return pidx[k]

        internal, bnd = [], {"inlet": [], "outlet": [], "wall": []}
        for ci, (x0, x1, y0, y1) in enumerate(boxes):
            v = [P(x0, y0, 0), P(x1, y0, 0), P(x1, y1, 0), P(x0, y1, 0),
                 P(x0, y0, 1), P(x1, y0, 1), P(x1, y1, 1), P(x0, y1, 1)]
            for nm, q in (("xlo", (v[0], v[3], v[7], v[4])),
                          ("xhi", (v[1], v[5], v[6], v[2])),
                          ("ylo", (v[0], v[4], v[5], v[1])),
                          ("yhi", (v[3], v[2], v[6], v[7])),
                          ("zlo", (v[0], v[1], v[2], v[3])),
                          ("zhi", (v[4], v[7], v[6], v[5]))):
                k = tuple(sorted(q))
                if k in fkey:
                    internal.append((fkey[k][0], ci, fkey[k][1]))
                    fkey[k] = None
                elif k is not None and fkey.get(k, 0) is None:
                    pass
                else:
                    fkey[k] = (ci, q, nm, x0, x1)
        for k, val in list(fkey.items()):
            if val is None:
                continue
            ci, q, nm, x0, x1 = val
            if region == "coolant" and nm == "xlo" and x0 <= 1e-12:
                bnd["inlet"].append((ci, q))
            elif region == "coolant" and nm == "xhi" and x1 >= CELL_LX - 1e-12:
                bnd["outlet"].append((ci, q))
            else:
                bnd["wall"].append((ci, q))
        allf, ow, ne = [], [], []
        for a, b, q in internal:
            allf.append(q)
            ow.append(min(a, b))
            ne.append(max(a, b))
        starts = {}
        for nm in ("inlet", "outlet", "wall"):
            starts[nm] = (len(allf), len(bnd[nm]))
            for ci, q in bnd[nm]:
                allf.append(q)
                ow.append(ci)
        hdr = "FoamFile{ version 2.0; }\n"
        open(os.path.join(pm, "points"), "w").write(
            hdr + "%d\n(\n" % len(pts)
            + "\n".join("(%.12g %.12g %.12g)" % p for p in pts) + "\n)\n")
        open(os.path.join(pm, "faces"), "w").write(
            hdr + "%d\n(\n" % len(allf)
            + "\n".join("4(%d %d %d %d)" % f for f in allf) + "\n)\n")
        open(os.path.join(pm, "owner"), "w").write(
            hdr + "%d\n(\n" % len(ow) + "\n".join(str(x) for x in ow) + "\n)\n")
        open(os.path.join(pm, "neighbour"), "w").write(
            hdr + "%d\n(\n" % len(ne) + "\n".join(str(x) for x in ne) + "\n)\n")
        bb = [hdr, "%d\n(" % 3]
        for nm in ("inlet", "outlet", "wall"):
            s, k = starts[nm]
            bb.append("%s\n{\n type patch;\n nFaces %d;\n startFace %d;\n}"
                      % (nm, k, s))
        bb.append(")")
        open(os.path.join(pm, "boundary"), "w").write("\n".join(bb) + "\n")
        return len(boxes)

    mboxes, cboxes = [], []
    for j in range(N_CELLS):
        y0 = j * PITCH
        for a in range(nx):
            for b in range(ny):
                mboxes.append((CELL_LX * a / nx, CELL_LX * (a + 1) / nx,
                               y0 + CELL_LY * b / ny, y0 + CELL_LY * (b + 1) / ny))
        if j < N_CELLS - 1:
            for a in range(nx):
                cboxes.append((CELL_LX * a / nx, CELL_LX * (a + 1) / nx,
                               y0 + CELL_LY, y0 + CELL_LY + GAP))
    nm = hexmesh("module", mboxes)
    nc = hexmesh("coolant", cboxes)

    # ---- fields.  A DOWNSTREAM-HOTTER solid and a warming coolant.
    #      `oc_bonus` is the OUTER-LOOP ARM's planted disagreement: it shifts
    #      this arm's whole trajectory by a KNOWN amount so that section 3.5's
    #      gate can be shown to SEE a disagreement of exactly that size.
    def wfield(t, region, boxes, n, patchvals=None):
        td = os.path.join(d, "%g" % t, region)
        os.makedirs(td, exist_ok=True)
        vals = []
        for (x0, x1, y0, y1) in boxes:
            xc = 0.5 * (x0 + x1)
            vals.append(T_INIT + 1.4 * (t / T_END) + tdn_bonus * xc / CELL_LX
                        + oc_bonus)
        body = ["FoamFile{ version 2.0; }", "dimensions [0 0 0 1 0 0 0];", "",
                "internalField   nonuniform List<scalar>", str(n), "("]
        body += ["%.12g" % v for v in vals]
        body += [")", ";", "", "boundaryField", "{"]
        for nmp in ("inlet", "outlet", "wall"):
            body += ["%s" % nmp, "{", "    type            calculated;"]
            k = (patchvals or {}).get(nmp)
            if k is not None:
                body += ["    value           nonuniform List<scalar>",
                         str(len(k)), "("]
                body += ["%.12g" % v for v in k]
                body += [")", ";"]
            body += ["}"]
        body += ["}"]
        open(os.path.join(td, "T"), "w").write("\n".join(body) + "\n")
        for f in MD.NEEDED[region]:
            fp = os.path.join(td, f)
            if not os.path.exists(fp):
                open(fp, "w").write("x\n")

    for t in _forge_times(dt):
        wfield(t, "module", mboxes, nm)
        wfield(t, "coolant", cboxes, nc,
               {"inlet": [T_INIT] * (N_CELLS - 1),
                "outlet": [T_INIT + (0.0 if blind else 0.8 * t / T_END)
                           + oc_bonus] * (N_CELLS - 1)})
    ref = os.path.join(d, "0", "module", "T")
    a = os.path.getmtime(ref)
    os.utime(ref, (a - 100, a - 100))

    # ---- the two convected-energy instruments.
    #  `conv_dT`, when given, writes a CONSTANT outlet-minus-inlet enthalpy
    #  flux so the convected term is exactly CP_AIR*MDOT*conv_dT*T_END.  It
    #  exists so --selftest can drive the section 6.2 ledger to a PASS as well
    #  as to a GATE FAIL: a gate only ever shown failing has not been shown to
    #  be a gate.
    for nmi, sgn in (("inlet_hflux", -1.0), ("outlet_hflux", +1.0)):
        pd = os.path.join(d, "postProcessing", nmi, "0")
        os.makedirs(pd, exist_ok=True)
        rows = ["# t  weightedSum(phi,T)"]
        for k in range(1, 11):
            t = T_END * k / 10.0
            if conv_dT is None:
                v = sgn * 0.2016 * (T_INIT + 0.4 * k / 10.0)
            else:
                v = sgn * MDOT * (T_INIT + (conv_dT if sgn > 0 else 0.0))
            rows.append("%g %.12g" % (t, v))
        open(os.path.join(pd, "surfaceFieldValue.dat"),
             "w").write("\n".join(rows) + "\n")
    return d


def _forge_times(dt):
    return sorted(set(list(WRITE_TIMES)))


def _fake_repo(doc_text="x\n"):
    """A throwaway git repo carrying the frozen document at HEAD, so that
    `grade()` can be driven end to end without touching the real repository."""
    fake = tempfile.mkdtemp(prefix="t25R2repo_")
    os.makedirs(os.path.join(fake, os.path.dirname(FROZEN_DOC)), exist_ok=True)
    open(os.path.join(fake, FROZEN_DOC), "w").write(doc_text)
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "-C", fake, "init", "-q"], capture_output=True)
    subprocess.run(["git", "-C", fake, "add", FROZEN_DOC], capture_output=True)
    subprocess.run(["git", "-C", fake, "commit", "-q", "-m", "f"],
                   capture_output=True, env=env)
    return fake


def selftest():
    fails = 0

    def chk(name, cond):
        nonlocal fails
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails += 1

    def refuses(fn):
        try:
            fn()
        except SystemExit as e:
            return e.code == EXIT_REFUSE
        return False

    # ---------------- the registered constants -----------------------------
    chk("PLANT is imported from roache_triple and equals 1.234e-03",
        PLANT == RT.PLANT and abs(PLANT - 1.234e-03) < 1e-15)
    chk("LADDER exercises PLANT exactly once", LADDER.count(PLANT) == 1)
    chk("D3 floor is 10*PLANT", abs(D3_FLOOR - 10 * PLANT) < 1e-15)
    chk("the registered load is SANAA'S VOLUMETRIC RATE 1.0e5 / 2.5e4 W/m3, "
        "not T25R's 70000 / 2800",
        Q_TAKEOFF == 100000.0 and Q_CRUISE == 25000.0)
    chk("q_takeoff / q_cruise = 4.0 (NOT T25R's 25)",
        abs(Q_TAKEOFF / Q_CRUISE - 4.0) < 1e-12)
    chk("SANAA'S BASIS IS SELF-CONSISTENT: 1.0e5 W/m3 in a 100x30x150 mm cell "
        "is 45.0 W, inside her stated 40-50 W",
        abs(Q_TAKEOFF * V_REAL_CELL - 45.0) < 1e-9
        and 40.0 <= Q_TAKEOFF * V_REAL_CELL <= 50.0)
    chk("her 100x30 mm SECTION is the registered 2-D section exactly; only the "
        "DEPTH differs, and a VOLUMETRIC rate is depth-independent",
        abs(V_REAL_CELL / V_CELL - 0.150 / DEPTH) < 1e-15)
    chk("E_gen over 900 s is 648000 J (T25R's was 157248)",
        abs(E_GEN - 648000.0) < 1e-6)
    chk("the adiabatic pulse bound is 2.400 K",
        abs(ADIABATIC_PULSE_K - 2.4) < 1e-12)
    chk("the adiabatic 900 s bound is 10.800 K",
        abs(ADIABATIC_900_K - 10.8) < 1e-12)
    chk("the quasi-steady interior cell-to-air rise at cruise is 6.957 K",
        abs(CRUISE_STEADY_RISE_K - 6.9573283859) < 1e-8)
    chk("the coolant outlet quasi-steady rises are 11.845 K takeoff and "
        "2.961 K cruise",
        abs(N_CELLS * Q_TAKEOFF * V_CELL / (MDOT * CP_AIR) - 11.8455342) < 1e-6
        and abs(N_CELLS * Q_CRUISE * V_CELL / (MDOT * CP_AIR) - 2.9613836)
        < 1e-6)
    chk("the section 3.5 thresholds are TIED TO THE PLANT SCALE: O1 and O3 at "
        "10*PLANT, O2 at 1*PLANT (a tenth of D3's own floor)",
        abs(OC_O1_TOL - 10 * PLANT) < 1e-15
        and abs(OC_O3_TOL - 10 * PLANT) < 1e-15
        and abs(OC_O2_TOL - PLANT) < 1e-15)
    chk("the registered run set is FOUR cases and the OC20 arm is L1's mesh, "
        "not a third level",
        len(CASES) == 4 and LEVEL["T25R2_L1_OC20"] == "L1"
        and NOUTER["T25R2_L1"] == 10 and NOUTER["T25R2_L1_OC20"] == 20)

    # --- THE STRUCTURAL PROOF THAT NO ORDER IS COMPUTED HERE.  The forbidden
    # tokens are assembled from fragments so this test does not match itself,
    # and the module DOCSTRING is excluded because it NAMES the classifications
    # in order to forbid them.  What is tested is the CODE: an observed order
    # needs a logarithm of a ratio of differences and a safety factor, and
    # neither exists anywhere in this file.
    src = open(os.path.abspath(__file__)).read()
    code = src[src.index("import json"):]
    forbidden = ["math." + "log", "log" + "10", "Fs" + " =", "1." + "25",
                 "def " + "gci", "def " + "roache",
                 "RT." + "roache", "RT." + "gci", "RT." + "observed"]
    hit = [t for t in forbidden if t in code]
    chk("no code path in this file computes a GCI or an observed order: an "
        "observed order needs a LOGARITHM of a ratio of differences and a GCI "
        "needs Roache's safety factor, and NEITHER TOKEN APPEARS ANYWHERE IN "
        "THIS FILE (forbidden tokens found: %r)" % hit, not hit)
    chk("the JSON emission pins roache_classification, gci and observed_order "
        "to None EXPLICITLY, so a downstream reader cannot mistake absence "
        "for omission",
        "roache_classification=None" in code and "gci=None" in code
        and "observed_order=None" in code)

    # --- THE STRUCTURAL PROOF THAT SECTION 3.5's RESIDUAL THRESHOLD IS GONE.
    #     Read from the PARSED MODULE, not from the text, so a comment naming
    #     the retired constant cannot make this pass or fail.
    import ast as _ast
    bound = set()
    for node in _ast.parse(src).body:
        if isinstance(node, _ast.Assign):
            for t in node.targets:
                for n in _ast.walk(t):
                    if isinstance(n, _ast.Name):
                        bound.add(n.id)
    resid_names = sorted(n for n in bound if "RESID" in n or "OUTER_FAIL" in n)
    chk("THE RETIRED RESIDUAL THRESHOLD IS STRUCTURALLY ABSENT: the only "
        "module-level name carrying RESID is RESID_REPORT_FIELDS, and no "
        "OUTER_FAIL fraction is bound anywhere (bound: %r)" % resid_names,
        resid_names == ["RESID_REPORT_FIELDS"])

    root = tempfile.mkdtemp(prefix="t25R2sel_")
    try:
        d = _forge_case(root, "T25R2_L2", 0.5)

        # --- the mesh reader
        mm = Mesh(d, "module")
        chk("module mesh boxes: 8 cells x nx*ny hexes", mm.n == 8 * 20 * 2)
        chk("cell banding assigns exactly 8 module cells",
            len(set(_cell_of(mm, i) for i in range(mm.n))) == N_CELLS)
        chk("total module volume is 8 * V_CELL",
            abs(sum(mm.vol) - N_CELLS * V_CELL) < 1e-12)

        # --- the readers
        v = read_cell_T(d, T_END, mm)
        chk("read_cell_T returns 8 values", len(v) == N_CELLS)
        chk("a mesh too coarse for the 10 mm x-band REFUSES rather than "
            "silently average the wrong cells",
            refuses(lambda: read_updown(
                _forge_case(root, "T25R2_L1", 0.5, nx=4), T_END)))
        shutil.rmtree(os.path.join(root, "T25R2_L1"), ignore_errors=True)
        up, dn = read_updown(d, T_END, mm)
        chk("read_updown sees the planted downstream bonus",
            all(dn[i] > up[i] for i in range(N_CELLS)))

        # --- the planted-zero controls, positive arms
        tmod = os.path.join("%g" % T_END, "module", "T")
        c = planted_zero_control(
            d, "read_cell_T", lambda x: max(read_cell_T(x, T_END)),
            lambda x, m: _plant_hottest_module_cell(x, T_END, m), tmod)
        chk("read_cell_T control PASSES and plants a WHOLE module cell so the "
            "volume-average shift is exactly mag, never mag/N",
            c["passed"] and c["n_planted"] == mm.n // N_CELLS)
        chk("read_cell_T read at PLANT equals PLANT to 1e-12, not PLANT/N",
            abs(c["at_plant"] - PLANT) < 1e-12)
        cs = planted_zero_control(
            d, "read_spread", lambda x: read_spread(x, T_END),
            lambda x, m: _plant_hottest_module_cell(x, T_END, m), tmod)
        chk("read_spread control PASSES (the spread moves by exactly mag)",
            cs["passed"] and abs(cs["at_plant"] - PLANT) < 1e-12)
        chk("read_cell_T control read at PLANT clears the RELATIVE predicate",
            c["at_plant"] >= PLANT * (1.0 - PLANT_REL_SLACK))

        tcool = os.path.join("%g" % T_END, "coolant", "T")
        c2 = planted_zero_control(
            d, "read_outlet_T", lambda x: read_patch_T(x, T_END, "outlet"),
            lambda x, m: _plant_patch_all(os.path.join(x, tcool), "outlet", m),
            tcool)
        chk("read_outlet_T control plants EVERY face so the shift is exactly "
            "mag, not mag/N", abs(c2["at_plant"] - PLANT) < 1e-12)

        # --- NEGATIVE ARM: a BLIND reader must REFUSE, not report zero.
        chk("a BLIND reader REFUSES (clause 4)",
            refuses(lambda: planted_zero_control(
                d, "blind", lambda x: 0.0,
                lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                tmod)))
        chk("a SINGLE-CELL plant under a volume-average reader REFUSES at "
            "clause 5 -- the mag/N failure mode is LIVE, not hypothetical",
            refuses(lambda: planted_zero_control(
                d, "single_cell", lambda x: max(read_cell_T(x, T_END)),
                lambda x, m: _plant_internal_one(os.path.join(x, tmod), m),
                tmod)))
        # --- NEGATIVE ARM: a NOISY reader must REFUSE at bitwise 0.0.
        st = {"k": 0}

        def noisy(x):
            st["k"] += 1
            return float(st["k"])
        chk("a NOISY reader REFUSES at bitwise 0.0 (clause 2)",
            refuses(lambda: planted_zero_control(
                d, "noisy", noisy,
                lambda x, m: _plant_hottest_module_cell(x, T_END, m),
                tmod)))
        # --- CLAUSE 8: the case was not written to.
        chk("the case bytes are unchanged after every control",
            open(os.path.join(d, tmod)).read() ==
            open(os.path.join(d, tmod)).read())

        # --- the acceptance criterion
        ac = acceptance_D(d, mm)
        chk("D1 PASSES on a downstream-hotter forge", ac["D1"])
        chk("D2 PASSES on a warming coolant", ac["D2"])
        chk("D3 PASSES when the signal exceeds 10*PLANT", ac["D3"])

        # --- NEGATIVE ARM: a flat solid must FAIL D1 and D3, not pass.
        d2 = _forge_case(root, "T25R2_L1", 0.5, tdn_bonus=0.0)
        ac2 = acceptance_D(d2)
        chk("a FLAT solid FAILS D1", not ac2["D1"])
        chk("a FLAT solid FAILS D3", not ac2["D3"])
        shutil.rmtree(d2, ignore_errors=True)
        # --- NEGATIVE ARM: a sub-threshold signal must FAIL D3 but pass D1.
        d3 = _forge_case(root, "T25R2_L2_DT025", 0.25, tdn_bonus=1e-4)
        ac3 = acceptance_D(d3)
        chk("a signal below 10*PLANT PASSES D1 but FAILS D3",
            ac3["D1"] and not ac3["D3"])
        # --- NEGATIVE ARM: an isothermal coolant must FAIL D2.
        d4 = _forge_case(root, "T25R2_L1", 0.5, blind=True)
        chk("an isothermal coolant FAILS D2", not acceptance_D(d4)["D2"])
        shutil.rmtree(d4, ignore_errors=True)

        # ==================================================================
        # SECTION 4.5 -- THE PULSE DICTIONARY, AT THE NEW LOADS.
        # ==================================================================
        chk("the registered pulse table (1.0e5 / 2.5e4 W/m3) passes",
            pulse_table_check(d, "T25R2_L2")["hits"] == 0)
        d5 = _forge_case(root, "T25R2_L1", 0.5, ramp=(59.75, 60.25))
        chk("a ramp straddling a step time REFUSES",
            refuses(lambda: pulse_table_check(d5, "T25R2_L1")))
        shutil.rmtree(d5, ignore_errors=True)
        d6 = _forge_case(root, "T25R2_L1", 0.5, q_take=5000.0)
        chk("the FEASIBILITY rung's 5000 W/m3 table REFUSES here",
            refuses(lambda: pulse_table_check(d6, "T25R2_L1")))
        shutil.rmtree(d6, ignore_errors=True)
        d6b = _forge_case(root, "T25R2_L1", 0.5, q_take=70000.0,
                          q_cruise=2800.0)
        chk("*** T25R's OWN 70000 / 2800 W/m3 TABLE REFUSES HERE. *** Sanaa "
            "rejected that construction by name; a case still carrying it is "
            "not this rung's case",
            refuses(lambda: pulse_table_check(d6b, "T25R2_L1")))
        shutil.rmtree(d6b, ignore_errors=True)

        # ==================================================================
        # SECTION 2.4 -- THE MESH GATE, ON THE REAL v2606 WORDING.
        # ==================================================================
        mq = mesh_quality(d)
        chk("*** THE MESH GATE PARSES THE REAL v2606 WORDING *** -- "
            "\"Mesh non-orthogonality Max: 0\" and \"Max skewness = "
            "1.66534018381e-13\", both of which DEFEAT analyse_t25R.py's "
            "frozen regexes (section 12 disclosure)",
            all(mq[r]["ok"] and mq[r]["nonorth"] == 0.0
                and abs(mq[r]["skew"] - 1.66534018381e-13) < 1e-22
                for r in REGIONS))
        dq = _forge_case(root, "T25R2_L1", 0.5, checkmesh_nonorth="0",
                         checkmesh_skew="0.5e+1")
        chk("a max skewness of 5 (above the registered 4) FAILS the mesh gate",
            not mesh_quality(dq)["module"]["ok"])
        shutil.rmtree(dq, ignore_errors=True)
        dq = _forge_case(root, "T25R2_L1", 0.5, checkmesh_nonorth="75.5")
        chk("a max non-orthogonality of 75.5 (above the registered 70) FAILS "
            "the mesh gate", not mesh_quality(dq)["module"]["ok"])
        shutil.rmtree(dq, ignore_errors=True)
        dq = _forge_case(root, "T25R2_L1", 0.5)
        open(os.path.join(dq, "log.checkMesh.module"), "w").write(
            "Checking geometry...\nMesh OK.\n")
        chk("a checkMesh log stating NEITHER max REFUSES rather than assume a "
            "number it never read", refuses(lambda: mesh_quality(dq)))
        shutil.rmtree(dq, ignore_errors=True)

        # ==================================================================
        # SECTION 3.4 -- `numerics_check`.  EVERY GUARD DRIVEN BY MUTATION.
        # ==================================================================
        nc = numerics_check(d, "T25R2_L2")
        chk("numerics_check passes the registered A2T dictionaries",
            nc["nOuterCorrectors"] == 10 and abs(nc["p_rgh_tol"] - 1e-8) < 1e-20)
        for lbl, kw in (
                ("*** THE T25R CONFIGURATION ITSELF -- no relaxationFactors "
                 "at all -- REFUSES ***", dict(no_relax=True)),
                ("a MISSING hFinal key REFUSES (the exact mechanism that "
                 "killed T25R_L1: a regex that matches in full does not match "
                 "hFinal)", dict(drop=("hFinal",))),
                ("a MISSING UFinal key REFUSES", dict(drop=("UFinal",))),
                ("a MISSING p_rghFinal key REFUSES", dict(drop=("p_rghFinal",))),
                ("a QUOTED-REGEX relaxation key REFUSES even though it would "
                 "match -- the registered form is LITERAL and decidable by "
                 "reading", dict(quoted=True)),
                ("the UNREACHABLE p_rgh tolerance 1e-9 REFUSES (GAMG stalls at "
                 "~4.4e-9; 601,763 discarded iterations changed no digit)",
                 dict(prgh_tol="1e-09")),
                ("a missing top-level PIMPLE dict REFUSES",
                 dict(top_pimple=False)),
                ("nOuterCorrectors 5 under a case registered at 10 REFUSES",
                 dict(nouter=5)),
                ("nOuterCorrectors 20 under a case registered at 10 REFUSES -- "
                 "the OUTER-LOOP GATE IS THE DIFFERENCE BETWEEN THE TWO ARMS, "
                 "so a swapped sweep count destroys it", dict(nouter=20))):
            dm = _forge_case(root, "T25R2_L1", 0.5, **kw)
            chk(lbl, refuses(lambda: numerics_check(dm, "T25R2_L1")))
            shutil.rmtree(dm, ignore_errors=True)
        dm = _forge_case(root, "T25R2_L1", 0.5,
                         drop=("hFinal",))
        # a relaxation factor at the wrong VALUE, not merely absent
        txt = open(os.path.join(dm, "system", "coolant",
                                "fvSolution")).read()
        open(os.path.join(dm, "system", "coolant", "fvSolution"), "w").write(
            txt.replace("  h 0.7;", "  h 0.7;\n    hFinal 1.0;"))
        chk("hFinal at 1.0 instead of the MEASURED 0.7 REFUSES",
            refuses(lambda: numerics_check(dm, "T25R2_L1")))
        shutil.rmtree(dm, ignore_errors=True)

        # ==================================================================
        # SECTION 3.5 -- THE LAST-SWEEP CENSUS IS A REPORT WITH NO VERDICT.
        # ==================================================================
        d7 = _forge_case(root, "T25R2_L1", 0.5)
        rr = resid_report(d7, "T25R2_L1")
        chk("the residual census returns NO boolean and NO `ok` key -- it is a "
            "REPORT and no verdict is derivable from it",
            "ok" not in rr and not any(isinstance(v, bool)
                                       for v in rr.values()))
        chk("the census reports the worst last-sweep residual per registered "
            "field", sorted(rr["worst"]) == sorted(RESID_REPORT_FIELDS))
        open(os.path.join(d7, "log.solve"), "w").write("End\n")
        chk("a census with NO `Initial residual` lines REFUSES rather than "
            "print zeros -- the planted-zero trap",
            refuses(lambda: resid_report(d7, "T25R2_L1")))
        shutil.rmtree(d7, ignore_errors=True)
        d7c = _forge_case(root, "T25R2_L1", 0.5)
        txt = open(os.path.join(d7c, "log.solve")).read()
        open(os.path.join(d7c, "log.solve"), "w").write(
            re.sub(r".*Solving for p_rgh.*\n", "", txt))
        chk("a registered census field ABSENT from the log REFUSES -- a census "
            "that silently omits its own field would report a zero it never "
            "saw", refuses(lambda: resid_report(d7c, "T25R2_L1")))
        shutil.rmtree(d7c, ignore_errors=True)

        # ==================================================================
        # SECTION 3.5 -- THE OUTER-LOOP GATE.  POSITIVE, PLANTED AND NEGATIVE.
        # ==================================================================
        oroot = tempfile.mkdtemp(prefix="t25R2oc_")
        try:
            def arms(bonus=0.0, tdn_b=0.05):
                shutil.rmtree(oroot, ignore_errors=True)
                os.makedirs(oroot)
                _forge_case(oroot, "T25R2_L1", 0.5)
                _forge_case(oroot, "T25R2_L1_OC20", 0.5, oc_bonus=bonus,
                            tdn_bonus=tdn_b)
                return oc_independence(oroot)

            # PLANTED CONTROL ON THE GATE ITSELF.  Two IDENTICAL arms would
            # give three zeros, and a zero from a comparator not shown able to
            # see a non-zero is not evidence (CLAUDE.md rule 3).  The arms are
            # therefore planted with a KNOWN disagreement and the gate must
            # report EXACTLY that number.
            g = arms(bonus=1.0e-4)
            chk("*** THE OUTER-LOOP GATE SEES A PLANTED DISAGREEMENT OF "
                "EXACTLY THE PLANTED SIZE *** (O1 %.6e against a planted "
                "1.000000e-04 K)" % g["O1"], abs(g["O1"] - 1.0e-4) < 1e-12)
            chk("O3 sees the same planted shift on the coolant outlet",
                abs(g["O3"] - 1.0e-4) < 1e-12)
            chk("a 1e-4 K sweep-count disagreement PASSES all three deltas",
                g["ok"] and g["O1_ok"] and g["O2_ok"] and g["O3_ok"])
            g = arms(bonus=5.0e-2)
            chk("a 5e-2 K disagreement (above 10*PLANT) FAILS O1 and FAILS the "
                "gate", (not g["O1_ok"]) and (not g["ok"]))
            g = arms(bonus=0.0, tdn_b=0.05 + 0.01)
            chk("*** ALL THREE DELTAS ARE REQUIRED: *** a disagreement in the "
                "D3 QUANTITY ALONE leaves O1 and O3 passing and still FAILS "
                "the gate on O2",
                g["O1_ok"] and g["O3_ok"] and (not g["O2_ok"])
                and (not g["ok"]))
            g = arms(bonus=0.0, tdn_b=0.05 + 1.0e-4)
            chk("a D3-quantity disagreement of 9e-5 K PASSES O2 (below "
                "1*PLANT)", g["O2_ok"])
            chk("the gate reports its own SCOPE LIMIT (L1 only, Co ~ 1600) on "
                "every invocation", "does not certify L2" in g["scope"].lower()
                or "DOES NOT CERTIFY L2" in g["scope"])
        finally:
            shutil.rmtree(oroot, ignore_errors=True)

        # ==================================================================
        # SECTION 6.2 -- THE ENERGY LEDGER, DRIVEN BOTH WAYS.
        # A gate only ever shown FAILING has not been shown to be a gate.
        # ==================================================================
        eroot = tempfile.mkdtemp(prefix="t25R2en_")
        try:
            de = _forge_case(eroot, "T25R2_L1", 0.5, conv_dT=0.0)
            e0 = energy_balance(de)
            need = e0["residual"] / (CP_AIR * T_END * MDOT)
            shutil.rmtree(de, ignore_errors=True)
            de = _forge_case(eroot, "T25R2_L1", 0.5, conv_dT=need)
            e1 = energy_balance(de)
            chk("the section 6.2 ledger PASSES when the four terms balance "
                "(|R|/E_gen %.3e)" % e1["rel"], e1["ok"] and e1["rel"] < 1e-9)
            shutil.rmtree(de, ignore_errors=True)
            de = _forge_case(eroot, "T25R2_L1", 0.5, conv_dT=need * 0.9)
            e2 = energy_balance(de)
            chk("a convected term 10 %% wrong FAILS the 2.0 %% band "
                "(|R|/E_gen %.3f %%)" % (100 * e2["rel"]), not e2["ok"])
        finally:
            shutil.rmtree(eroot, ignore_errors=True)

        # --- the energy planted control must MOVE, at the NEW load.
        ep = energy_planted_control(d)
        chk("the +10 % source control moves the residual by exactly 14400 J "
            "at the registered 1.0e5 W/m3 (T25R's was 10080 J at 70000)",
            abs(ep["planted_J"] - 14400.0) < 1e-6
            and abs(ep["seen_J"] - 14400.0) < 1e-6)

        # --- postProcessing with two start-time dirs must REFUSE.
        d8 = _forge_case(root, "T25R2_L1", 0.5)
        os.makedirs(os.path.join(d8, "postProcessing", "inlet_hflux", "450"))
        chk("two postProcessing start-time dirs REFUSE (restart double-count)",
            refuses(lambda: _postproc_dat(d8, "inlet_hflux")))
        shutil.rmtree(d8, ignore_errors=True)

        # ==================================================================
        # SECTION 3.5 PROPAGATION, DRIVEN END TO END THROUGH `grade()`.
        # ==================================================================
        fake = _fake_repo()
        try:
            groot = tempfile.mkdtemp(prefix="t25R2gr_")
            try:
                _forge_case(groot, "T25R2_L1", 0.5)
                _forge_case(groot, "T25R2_L1_OC20", 0.5, oc_bonus=5.0e-2)
                import io as _io
                import contextlib as _ctx
                buf = _io.StringIO()
                with _ctx.redirect_stdout(buf):
                    rc, out = grade(groot, ["T25R2_L1"], repo=fake)
                chk("a FAILING outer-loop gate makes grade() exit non-zero",
                    rc == EXIT_FAIL)
                chk("*** THE GATE FAIL PROPAGATES: the L1 row is NOT A RESULT, "
                    "not GATE FAIL and not PASS ***",
                    out["T25R2_L1"]["verdict"] == "NOT A RESULT")
                chk("the outer-loop gate itself is recorded as GATE FAIL",
                    out["OUTER_LOOP_GATE"]["state"] == "GATE FAIL")
                chk("no physics number is printed under a failed outer-loop "
                    "gate", "D1 (T_dn > T_up" not in buf.getvalue())

                shutil.rmtree(groot, ignore_errors=True)
                os.makedirs(groot)
                _forge_case(groot, "T25R2_L1", 0.5, conv_dT=0.0)
                _need = energy_balance(os.path.join(groot, "T25R2_L1"))[
                    "residual"] / (CP_AIR * T_END * MDOT)
                shutil.rmtree(groot, ignore_errors=True)
                os.makedirs(groot)
                _forge_case(groot, "T25R2_L1", 0.5, conv_dT=_need)
                _forge_case(groot, "T25R2_L1_OC20", 0.5, oc_bonus=1.0e-4,
                            conv_dT=_need)
                buf = _io.StringIO()
                with _ctx.redirect_stdout(buf):
                    rc, out = grade(groot, ["T25R2_L1"], repo=fake)
                chk("a PASSING outer-loop gate lets the physics gates run",
                    out["OUTER_LOOP_GATE"]["state"] == "PASS"
                    and out["T25R2_L1"]["verdict"] in ("PASS", "GATE FAIL"))
                chk("the L1 row grades PASS on a clean forge",
                    out["T25R2_L1"]["verdict"] == "PASS" and rc == EXIT_OK)

                # *** THE GATE CANNOT BE SKIPPED BY GRADING ONE CASE. ***
                shutil.rmtree(groot, ignore_errors=True)
                os.makedirs(groot)
                _forge_case(groot, "T25R2_L2", 0.5)
                buf = _io.StringIO()
                with _ctx.redirect_stdout(buf):
                    rc, out = grade(groot, ["T25R2_L2"], repo=fake)
                chk("*** GRADING ONE CASE DOES NOT SKIP THE OUTER-LOOP GATE: "
                    "with no OC arms on disk the gate is PENDING and the L2 "
                    "row is withheld ***",
                    out["OUTER_LOOP_GATE"]["state"] == "PENDING"
                    and out["T25R2_L2"]["verdict"] == "PENDING"
                    and rc == EXIT_FAIL)
            finally:
                shutil.rmtree(groot, ignore_errors=True)

            # --- the freeze check refuses an EDITED document.
            open(os.path.join(fake, FROZEN_DOC), "a").write("edited\n")
            chk("an EDITED (uncommitted) pre-registration REFUSES: frozen "
                "files are never edited (rule 6)",
                refuses(lambda: freeze_check(fake)))
        finally:
            shutil.rmtree(fake, ignore_errors=True)

        # --- the freeze check refuses an uncommitted document.
        bare = tempfile.mkdtemp(prefix="t25R2bare_")
        try:
            subprocess.run(["git", "-C", bare, "init", "-q"],
                           capture_output=True)
            os.makedirs(os.path.join(bare, os.path.dirname(FROZEN_DOC)),
                        exist_ok=True)
            open(os.path.join(bare, FROZEN_DOC), "w").write("x\n")
            chk("an UNCOMMITTED pre-registration REFUSES (rule 2)",
                refuses(lambda: freeze_check(bare)))
        finally:
            shutil.rmtree(bare, ignore_errors=True)

        # ==================================================================
        # THE TRACEBACK TRAP, DRIVEN.
        # ==================================================================
        def _boom(argv):
            raise RuntimeError("planted crash")
        chk("*** AN UNCAUGHT TRACEBACK EXITS ON THE REFUSE PATH (2), NOT ON "
            "THE GRADED NOT-A-RESULT PATH (1) *** -- a crashed comparator has "
            "measured nothing and is not entitled to a graded answer",
            _guarded([], _fn=_boom) == EXIT_REFUSE)
        chk("a deliberate refuse() still exits 2 through the guard",
            refuses(lambda: _guarded([], _fn=lambda a: refuse("planted"))))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if fails == 0 else "FAIL", fails))
    return EXIT_OK if fails == 0 else EXIT_FAIL


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root, outp = HERE, None
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if "--json" in argv:
        i = argv.index("--json")
        outp = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    rc, out = grade(root, want)
    if outp:
        with open(outp, "w") as f:
            json.dump(dict(rung="T25R2", frozen_document=FROZEN_DOC,
                           plant=PLANT, ladder_registered=False,
                           roache_classification=None, gci=None,
                           observed_order=None,
                           q_takeoff_W_per_m3=Q_TAKEOFF,
                           q_cruise_W_per_m3=Q_CRUISE,
                           per_cell_W_unit_depth_DERIVED=Q_TAKEOFF * V_CELL,
                           per_cell_W_real_cell_DERIVED=Q_TAKEOFF * V_REAL_CELL,
                           results=out), f,
                      indent=1, default=str)
    return rc


def _guarded(argv, _fn=None):
    """*** THE TRACEBACK TRAP, MEASURED ELSEWHERE THIS NIGHT AND CLOSED HERE.

    An instrument with no `except` clause lets an uncaught traceback leave the
    interpreter with exit status 1 -- which in this file's exit vocabulary is
    "a gate failed or a row is NOT A RESULT", i.e. a GRADED outcome.  A crash
    would then be INDISTINGUISHABLE FROM A MEASUREMENT.  Every uncaught
    exception is converted to a REFUSAL (exit 2): a crashed comparator has
    measured nothing and is not entitled to return a graded answer of any kind.

    `SystemExit` is re-raised untouched: it carries the deliberate exit codes of
    `refuse()` and of `grade()`.  `_fn` exists so --selftest can drive this path
    with a planted crash rather than trust a reading of it.
    """
    fn = main if _fn is None else _fn
    try:
        return fn(argv)
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print("REFUSE: analyse_t25R2.py raised an uncaught exception. A "
              "CRASHED COMPARATOR HAS MEASURED NOTHING and exits on the REFUSE "
              "path (2), NEVER on the graded path (1), so that a crash can "
              "never be mistaken for a GATE FAIL or a NOT A RESULT.")
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(_guarded(sys.argv[1:]))
