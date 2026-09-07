"""LR1 comparator: the a-posteriori secondary-velocity grade on the square-duct
model-form ladder (SST-linear vs corrections), AR_1_Ret_360.

THIS IS A DRAFT INSTRUMENT.  LR1's PREREGISTRATION.md is
`prereg_commit: PENDING_SUPERVISOR_FREEZE`; every threshold below carries the
`DRAFT PENDING-FREEZE` marker and is bound to a value only at the LR1 freeze
commit, whose message will carry the sha256 of this file (PREREGISTRATION.md
§8(b)).  Nothing here is believed until the supervisor diff-reads it personally
(SUPERVISION §3 check 1) and demonstrates its planted-zero control able to fail.

The load-bearing quantity is the peak in-plane secondary-velocity magnitude
`|U_sec|_max = max_cells sqrt(V^2 + W^2)`, reported as `|U_sec|_max / U_bulk`
(PREREGISTRATION.md §3.1 M-bin).  Two channels per model:

  * BINARY (§3.1): does the model cross the linear-null FLOOR?  This is the
    certified headline -- a qualitative claim that needs no band and is NOT
    Roache-gated (a linear model's in-plane field is machine noise at the null,
    §6.3, so its quantitative triple is meaningless and cannot overturn the
    baseline prediction).
  * QUANTITATIVE (§3.2 / §3.3): for a recovering model (above the floor), the
    metric is Roache-gated over the G2 triple L1/L2/L3 IN FULL under standing
    rule 5, and only a CONVERGING triple's extrapolated fine scalar `f_ext`
    reaches the DNS band.  Route 1 of §4.3: `f_ext` is compared to the DNS
    scalar 0.0205 with NO interpolation between the model mesh and the DNS mesh.

Standing rule 5 is enforced structurally, not remembered: `roache()` returns
before computing p / f_ext / GCI on any branch that is not CONVERGING, and the
quantitative verdict returns NOT A RESULT on a non-CONVERGING triple before any
band test.  The gate can only turn a PASS or GATE FAIL INTO NOT A RESULT.

Refusals are `raise` / `sys.exit(2)`, never `assert` (L-332): `python3 -O`
deletes every assert.  This module parses its own AST and refuses if it holds a
single `ast.Assert` node, the counter first shown able to count a planted one.

WHAT THIS INSTRUMENT DOES NOT DO (honest scope, for the supervisor):
  * It does not implement the corner-vortex TOPOLOGY count (the second half of
    §3.1's M-bin).  That needs a vortex-detection pass over the full in-plane
    field and is emitted as a PENDING sub-channel, exactly as §4.3 permits the
    pointwise profile route to be PENDING when intractable.  The binary's
    floor-crossing component IS computed; its topology component is not closed
    here.
  * It does not implement the pointwise corner-bisector profile route (§4.3
    route 2); that route is PENDING by the pre-registration's own allowance.
  * It grades no GP model: rung 4 is BLOCKED (capability-absent, §1.4), a
    registered verdict, not a non-result.
"""

import ast
import contextlib
import hashlib
import io
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

# ==========================================================================
# DRAFT REGISTRY -- PENDING-FREEZE.  Bound at the LR1 freeze commit by sha256.
# ==========================================================================

# Run-directory layout, PREREGISTRATION.md §8(c):
#   /home/ubuntu/closure-data/lr1/<model>/{L1,L2,L3}
RUN_ROOT = Path("/home/ubuntu/closure-data/lr1")

# The grid triple is G2's, REUSED byte-for-byte (§2.2).  coarse -> fine.
# Roache indices: 1 = finest = L3, 2 = L2, 3 = coarsest = L1.
# endTimes are G2's, held FIXED per level for every model (§3.3): lengthening
# endTime after seeing a model did not converge is tuning against the answer.
LEVELS = (
    ("L1", 1024, 20000),
    ("L2", 4096, 30000),
    ("L3", 16384, 40000),
)
D_SPATIAL = 2
R21 = 2.0          # h(L2)/h(L3)
R32 = 2.0          # h(L1)/h(L2)

# ---- DRAFT threshold constants -- PENDING-FREEZE -------------------------
# Each of these is a DRAFT bound only at the LR1 freeze commit by sha256
# (PREREGISTRATION.md §5, §8(b)); the supervisor sets or confirms them there.
FS = 1.25                          # DRAFT PENDING-FREEZE -- Roache factor of safety (§2.2)
U_BULK = 85.395                    # DRAFT PENDING-FREEZE -- Re_b*nu/h, m/s (§2.1)
FLOOR = 1.0e-3                     # DRAFT PENDING-FREEZE -- linear-null binary floor on
                                   #   |U_sec|_max/U_bulk (§3.1); 0.1 % of bulk
DNS_USEC_OVER_UBULK = 0.0205       # DRAFT PENDING-FREEZE -- lab DNS |U_sec|_max/U_bulk (§3.2)
BAND = (0.0123, 0.0287)            # DRAFT PENDING-FREEZE -- acceptance band on f_ext,
                                   #   DNS 0.0205 +/- 40 % relative (§3.2); see the
                                   #   RECONCILIATION FLAG in §3.2 (BASELINES.md "1.5 %"
                                   #   vs the measured peak 2.05 %) -- the supervisor
                                   #   reconciles the two statistics at freeze.

# Roache classification floor for EXACT/STAGNANT detection on the QUANTITATIVE
# metric.  This is NOT the linear-null FLOOR above; it is the small difference
# below which two levels are indistinguishable.  DRAFT PENDING-FREEZE.
ROACHE_FLOOR_MODE = "rel"
ROACHE_FLOOR = 1.0e-6              # DRAFT PENDING-FREEZE

# Iterative-convergence residual ceilings (§6.3), drafted against G2's measured
# floors and set from measurement at freeze, NOT borrowed.  DRAFT PENDING-FREEZE.
RES_MAX = {"Ux": 1e-6, "k": 5e-6, "omega": 5e-6, "epsilon": 5e-6}   # DRAFT PENDING-FREEZE
RES_DIAGNOSTIC = ("Uy", "Uz", "p")
# The |U_sec|_max plateau over the final PLATEAU_TAIL_FRAC of WRITTEN time dirs
# (§6.3).  The write cadence per level is an OPEN budget question (§3.3): if the
# solver writes only at endTime there is a single write point and IC2 refuses.
# MIN_USEC_POINTS and PLATEAU_RTOL are DRAFT PENDING-FREEZE.
PLATEAU_TAIL_FRAC = 0.10
PLATEAU_RTOL = 1.0e-5             # DRAFT PENDING-FREEZE
MIN_USEC_POINTS = 3              # DRAFT PENDING-FREEZE

# ---- per-model registry (§1.1, §1.3, §6.2) -------------------------------
# Required-field list is PER MODEL: U p k, plus omega OR epsilon per model, plus
# nut, plus the stress field R for the RSMs (§6.2).  "scale" names the second
# transport variable.  "rsm" adds R.  All nine models run rung 1 (8) + rung 3 (1)
# on the triple = 27 solves (§1.5); GP (rung 4) is BLOCKED and not listed here.
MODELS = (
    # name,               scale,      rsm,   rung, class
    ("kOmegaSST",        "omega",   False, 1, "linear EVM"),
    ("realizableKE",     "epsilon", False, 1, "linear EVM"),
    ("kEpsilon",         "epsilon", False, 1, "linear EVM"),
    ("ShihQuadraticKE",  "epsilon", False, 1, "nonlinear (quadratic) EVM"),
    ("LienCubicKE",      "epsilon", False, 1, "nonlinear (cubic) EVM"),
    ("LienLeschziner",   "epsilon", False, 1, "nonlinear EVM"),
    ("LRR",              "epsilon", True,  1, "RSM"),
    ("SSG",              "epsilon", True,  1, "RSM"),
    ("kOmegaSSTQCR",     "omega",   False, 3, "SST + QCR2000"),
)

AGE_MARKER = "0/U"                 # touched LAST at launch; dates the run (§6.2)

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$")

# ---- planted-control constants (§6.1) ------------------------------------
# A corner cell's (V, W) is set to (PLANT_V, PLANT_W) so |U_sec|_max takes the
# KNOWN value sqrt(V^2 + W^2) = 5.0 m/s exactly (a 3-4-5 triple), an order of
# magnitude above any other cell's in-plane field in the base, so it is the max.
PLANT_V = 3.0
PLANT_W = 4.0
PLANT_USEC = math.hypot(PLANT_V, PLANT_W)     # 5.0 m/s, the known planted maximum
PLANT_RTOL = 1e-12
CONTROL_NCELLS = 16                            # synthetic control mesh, kept small

# The FOAM-fatal reader, LINE-ANCHORED so OpenFOAM's own `trapFpe:` startup
# banner cannot make it fire (the G2 lesson, grade_g2.py:129-140).  Five
# channels; `trapping enabled` matches none of them.  Exercised in BOTH
# directions by `planted_control_fatal` (standing rule 3).
FATAL_RE = re.compile(
    r"-->\s*FOAM FATAL(?:\s+IO)?\s+ERROR"
    r"|FOAM exiting"
    r"|Foam::sig\w+::sigHandler"
    r"|Foam::error::printStack"
    r"|^(?:Floating point exception|Segmentation fault)",
    re.MULTILINE)
FPE_BANNER = "trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).\n"

NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


class Refusal(Exception):
    """A condition that must stop this instrument under ANY interpreter flag."""


def refuse(msg):
    raise Refusal(msg)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def req_fields(scale, rsm):
    """Per-model required-field list at endTime (§6.2)."""
    fields = ["U", "p", "k", scale, "nut"]
    if rsm:
        fields.append("R")
    return fields


def req_res(scale):
    """Per-model iterative-convergence residual channels (§6.3)."""
    return ("Ux", "k", scale)


# ==========================================================================
# L-332 control -- the counter is first shown able to count a planted assert.
# ==========================================================================
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse("AST-CONTROL: the counter returned %d on a snippet holding exactly "
               "one assert; its zero here would be a blind spot, not a reading."
               % planted)
    own = count_asserts(Path(__file__).read_text())
    if own != 0:
        refuse("AST-CONTROL: this module holds %d ast.Assert node(s); python3 -O "
               "deletes every one (L-332). Refusals must be raise / sys.exit(2)."
               % own)
    return planted, own


# ==========================================================================
# The production reader.  read_Usec is THE function the planted controls
# exercise; it is a pure-python OpenFOAM-ASCII reader in the grade_g2.py style
# (no numpy), so the supervisor's diff-read compares against a known pattern.
# ==========================================================================
def _read(path):
    path = Path(path)
    if not path.is_file():
        refuse("READER: %s does not exist" % path)
    return path.read_text(errors="replace")


def _strip_header(text):
    """Drop the FoamFile header block so its keywords are not read as data."""
    m = re.search(r"(?m)^FoamFile\s*$", text)
    if m is None:
        return text
    ob = text.find("{", m.end())
    if ob < 0:
        return text
    depth = 0
    for i in range(ob, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:]
    return text


def read_Usec(path, ncells):
    """|U_sec|_max = max over cells of sqrt(V^2 + W^2) from a volVectorField U.

    Components 2 and 3 of each vector are the in-plane secondary velocities
    (V, W); component 1 is the streamwise Ux (PREREGISTRATION.md §2.1).  Reads a
    solver-WRITTEN internalField (a resolved numeric field), uniform or
    nonuniform List<vector>, length-checked against ncells; refuses on any
    length mismatch rather than padding.  This targets solver output, not the
    macro-laden 0/U input (which carries `internalField uniform $Uinlet`).
    """
    body = _strip_header(_read(path))
    u = re.search(r"(?m)^\s*internalField\s+uniform\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)"
                  % (NUM, NUM, NUM), body)
    if u is not None:
        v, w = float(u.group(2)), float(u.group(3))
        return math.hypot(v, w)
    nu = re.search(r"(?m)^\s*internalField\s+nonuniform\s+List<vector>\s*\n?\s*(\d+)"
                   r"\s*\n\(", body)
    if nu is None:
        refuse("READER: %s has neither a uniform nor a nonuniform vector "
               "internalField" % path)
    n = int(nu.group(1))
    start = nu.end()
    close = body.find("\n)", start)
    if close < 0:
        refuse("READER: %s has an unterminated internalField list" % path)
    trips = [tuple(float(x) for x in t.split())
             for t in re.findall(r"\(([^)]*)\)", body[start:close])]
    if len(trips) != n:
        refuse("READER: %s declares %d vectors and holds %d" % (path, n, len(trips)))
    if n != ncells:
        refuse("READER: %s holds %d vectors, the mesh has %d cells" % (path, n, ncells))
    mx = 0.0
    for t in trips:
        if len(t) != 3:
            refuse("READER: %s holds a non-3-component vector entry" % path)
        mx = max(mx, math.hypot(t[1], t[2]))
    return mx


def _write_U(vectors):
    """A minimal volVectorField U in the solver-written dialect read_Usec parses."""
    return ("FoamFile\n{\n    version 2.0;\n    format ascii;\n"
            "    class volVectorField;\n    object U;\n}\n\n"
            "dimensions      [0 1 -1 0 0 0 0];\n\n"
            "internalField   nonuniform List<vector> \n%d\n(\n%s\n)\n;\n\n"
            "boundaryField\n{\n}\n"
            % (len(vectors), "\n".join("(%.17g %.17g %.17g)" % v for v in vectors)))


# ==========================================================================
# PLANTED-ZERO CONTROL (standing rule 3, §6.1) -- recovery + inverse + blind.
# Each writes a REAL file and reads it back through read_Usec, the SAME function
# used on the real data, and REFUSES on invisibility.
# ==========================================================================
def _base_and_planted(ncells):
    """A base U field with zero in-plane velocity everywhere and a copy with one
    corner cell's (V, W) set to the plant.  Returns (base, planted, corner_idx)."""
    base = [(10.0, 0.0, 0.0) for _ in range(ncells)]     # streamwise only; null secondary
    corner = 0                                            # a corner cell
    planted = list(base)
    planted[corner] = (10.0, PLANT_V, PLANT_W)
    return base, planted, corner


def _recovery_check(reader, path, ncells, want, who):
    """The check the plant exists to make: `reader` must return the planted max."""
    got = reader(path, ncells)
    if abs(got - want) > PLANT_RTOL * abs(want):
        refuse("%s: a field whose |U_sec|_max is the planted %.9e read back as "
               "%.9e; the reader cannot see the value it is asked to report"
               % (who, want, got))
    return got


def planted_zero_control(tmp, ncells=CONTROL_NCELLS):
    base, planted, corner = _base_and_planted(ncells)
    base_text, planted_text = _write_U(base), _write_U(planted)
    # (2) the substitution must have changed bytes, or the plant was never written
    if base_text == planted_text:
        refuse("PLANT Usec: setting corner cell %d to (V,W)=(%.3g,%.3g) changed no "
               "bytes; the plant was never written and its recovery would prove "
               "nothing" % (corner, PLANT_V, PLANT_W))
    pp = Path(tmp) / "planted_U"
    pp.write_text(planted_text)
    # (1) the production reader must return the planted maximum
    got = _recovery_check(read_Usec, pp, ncells, PLANT_USEC, "PLANT Usec")
    # (3) inverse: the same reader on the UNPLANTED file must NOT return the plant
    bp = Path(tmp) / "base_U"
    bp.write_text(base_text)
    base_max = read_Usec(bp, ncells)
    if abs(base_max - PLANT_USEC) <= PLANT_RTOL * abs(PLANT_USEC):
        refuse("PLANT Usec inverse: read_Usec returns the plant on the UNPLANTED "
               "file (|U_sec|_max=%.9e); it is a constant, not a reader" % base_max)
    # (4) blind control: a reader that returns 0.0 for every cell MUST be caught by
    #     the recovery check.  If it is not, the recovery check is a no-op and the
    #     near-zero the real reader gives a linear-null model would be a blind spot
    #     rather than a reading (a-zero-needs-a-live-planted-control).
    def _blind(_path, _ncells):
        return 0.0
    try:
        _recovery_check(_blind, pp, ncells, PLANT_USEC, "BLIND")
    except Refusal:
        blind_fired = True
    else:
        refuse("BLIND CONTROL: a reader returning 0.0 for every cell was NOT caught "
               "against the planted %.9e; the recovery check is a no-op, so a "
               "linear-null model's near-zero would be a blind spot" % PLANT_USEC)
    return PLANT_USEC, got, base_max, blind_fired


# ==========================================================================
# log parsing (adapted from grade_g2.py; LR1 has no gradP channel).
# ==========================================================================
def parse_log(path):
    """Parse log.run.  An ABSENT log is REPORTED, never refused: a level with no
    solver log is an incomplete level and rule 5 step 1 already grades it
    NOT A RESULT (the grade_g2.py departure from grade_g1.py, §6.3)."""
    path = Path(path)
    if not path.is_file():
        return {"absent": True, "end": False, "fatal": False, "libs_warning": False,
                "exec_count": -1, "n_time_blocks": 0, "final_res": {},
                "final_exec_s": None}
    text = _read(path)
    blocks = [m.start() for m in re.finditer(r"(?m)^Time = ", text)]
    last = text[blocks[-1]:] if blocks else ""
    final_res = {}
    for name in tuple(RES_MAX) + RES_DIAGNOSTIC:
        m = re.search(r"Solving for %s, Initial residual = (%s)" % (re.escape(name), NUM),
                      last)
        if m is not None:
            final_res[name] = float(m.group(1))
    execs = re.findall(r"ExecutionTime = (%s) s" % NUM, text)
    return {
        "absent": False,
        "end": bool(re.search(r"(?m)^End\s*$", text)),
        "fatal": bool(FATAL_RE.search(text)),
        "libs_warning": "Could not load" in text,
        "exec_count": len(re.findall(r"ExecutionTime = ", text)),
        "n_time_blocks": len(blocks),
        "final_res": final_res,
        "final_exec_s": float(execs[-1]) if execs else None,
    }


def planted_control_fatal():
    """Standing rule 3 for the FOAM-fatal reader, in BOTH directions (grade_g2.py
    pattern): a genuine FATAL block and a fired sigFpe read as fatal, while a
    CLEAN log carrying OpenFOAM's `trapFpe:` banner verbatim reads NOT fatal.
    A detector never shown able to return NOT-fatal is a constant."""
    prologue = ("Exec   : simpleFoam -case .\nHost   : ip-172-31-43-247\n"
                "nProcs : 1\n" + FPE_BANNER + "memory pool : not available\n\n")
    body = ("Time = 1\nDILUPBiCGStab:  Solving for Ux, Initial residual = 1e-14, "
            "Final residual = 1e-16, No Iterations 1\n"
            "ExecutionTime = 1 s  ClockTime = 1 s\n\n")
    with tempfile.TemporaryDirectory(prefix="lr1fatal_") as td:
        td = Path(td)
        a = td / "foam_fatal.run"
        a.write_text(prologue + body + "--> FOAM FATAL ERROR: (openfoam-2606)\n"
                     "Maximum number of iterations exceeded\n\nFOAM exiting\n\n")
        if not parse_log(a)["fatal"]:
            refuse("PLANT fatal(a): a genuine `--> FOAM FATAL ERROR` block + "
                   "`FOAM exiting` was read as NOT fatal")
        b = td / "sigfpe.run"
        b.write_text(prologue + body + "#0  Foam::error::printStack(Foam::Ostream&)\n"
                     "#1  Foam::sigFpe::sigHandler(int)\n"
                     "Floating point exception (core dumped)\n")
        if not parse_log(b)["fatal"]:
            refuse("PLANT fatal(b): a fired sigFpe handler with its stack was read "
                   "as NOT fatal")
        c = td / "clean_banner.run"
        c.write_text(prologue + body + "End\n")
        if FPE_BANNER not in c.read_text():
            refuse("PLANT fatal(c): the banner is not in the file on disk")
        cp = parse_log(c)
        if cp["absent"] or not cp["end"]:
            refuse("PLANT fatal(c): the clean control was not read as a present log "
                   "with an End line; its NOT-fatal would be a blind spot")
        if cp["fatal"]:
            refuse("PLANT fatal(c): a CLEAN log whose only match is OpenFOAM's own "
                   "`trapFpe:` banner was read as FATAL; a detector that cannot "
                   "return NOT-fatal is a constant")
        return True, True, cp["fatal"]


# ==========================================================================
# strict completion, per (model x level).  PHYSICS clauses REFUSE (block the
# model -> NOT A RESULT via rule 5 step 1); INFRASTRUCTURE clauses are named and
# recorded and void nothing (L-342).
# ==========================================================================
def completion(case, end, ncells, fields):
    case = Path(case)
    phys, infra = [], []

    rcp = case / "rc.txt"
    if not rcp.is_file():
        phys.append("P1 rc: %s absent" % rcp)
    else:
        rc = rcp.read_text().strip()
        if rc != "0":
            phys.append("P1 rc: solver rc = %s (a non-zero rc is a finding)" % rc)

    log = parse_log(case / "log.run")
    if log["absent"]:
        phys.append("P2 End: %s does not exist; the level has no solver log, so it "
                    "is incomplete and rule 5 step 1 applies" % (case / "log.run"))
    elif not log["end"]:
        phys.append("P2 End: log.run holds no `End` line")
    if log["fatal"]:
        phys.append("P3 fatal: log.run holds a FOAM FATAL / FPE / signal line")

    times = sorted((c.name for c in case.iterdir()
                    if c.is_dir() and TIME_DIR.match(c.name)), key=float)
    if not times:
        phys.append("P4 time dirs: none")
    elif float(times[-1]) != float(end):
        phys.append("P4 last time: %s, registered endTime %s" % (times[-1], end))

    d = case / str(end)
    missing = [f for f in fields if not (d / f).is_file()]
    if missing:
        phys.append("P5 fields at endTime: missing %r (per-model required set %r)"
                    % (missing, fields))

    marker = case / AGE_MARKER
    if not marker.is_file():
        phys.append("P6 age guard: marker %s absent" % marker)
    elif not missing:
        t0 = marker.stat().st_mtime
        stale = [f for f in fields if (d / f).stat().st_mtime <= t0]
        if stale:
            phys.append("P6 age guard: %r at endTime are NOT strictly newer than %s; "
                        "they cannot be the answer this run produced" % (stale, AGE_MARKER))

    if not log["absent"] and log["exec_count"] != int(end):
        phys.append("P7 ExecutionTime lines: %d, registered endTime %d. HARD "
                    "EQUALITY, no tolerance; a mismatch is triaged by the "
                    "supervisor, never reclassified here"
                    % (log["exec_count"], int(end)))

    cm = case / "log.checkMesh"
    if not cm.is_file() or "Mesh OK" not in cm.read_text(errors="replace"):
        infra.append("I1 checkMesh: log absent or not `Mesh OK`")
    mt = case / "mem_time.txt"
    if not mt.is_file() or "Maximum resident set size" not in mt.read_text(errors="replace"):
        infra.append("I2 MaxRSS: no /usr/bin/time -v reading recorded")
    if not (case / "wall_s.txt").is_file():
        infra.append("I3 wall_s: not recorded; the cost calibration has no actual")
    if log["libs_warning"]:
        infra.append("I5 libs: the solver could not load a library named in the "
                     "shipped controlDict; the entry is kept, never deleted to tidy "
                     "a case (standing rule 14)")
    return phys, infra, log


def iterative_residual(log, channels):
    """IC1: the per-model required residual channels below their ceilings (§6.3)."""
    fails, diag = [], {}
    for name in channels:
        if name not in log["final_res"]:
            fails.append("IC1 residual: no `Solving for %s` in the final Time block"
                         % name)
        elif log["final_res"][name] > RES_MAX[name]:
            fails.append("IC1 residual: %s final initial-residual %.3e > registered "
                         "%.0e" % (name, log["final_res"][name], RES_MAX[name]))
    for name in RES_DIAGNOSTIC:
        diag[name] = log["final_res"].get(name)
    return fails, diag


def usec_history(case, ncells):
    """|U_sec|_max at every WRITTEN non-zero time directory, in time order."""
    case = Path(case)
    times = sorted((c.name for c in case.iterdir()
                    if c.is_dir() and TIME_DIR.match(c.name) and float(c.name) > 0.0),
                   key=float)
    hist = []
    for t in times:
        up = case / t / "U"
        if up.is_file():
            hist.append((float(t), read_Usec(up, ncells)))
    return hist


def iterative_plateau(hist):
    """IC2: |U_sec|_max plateaued over the final PLATEAU_TAIL_FRAC of writes (§6.3).

    For a linear-null model this is trivially satisfied at the noise floor and the
    binary reads `null`; for a recovering model it gates the signal.  The write
    cadence is an open budget question (§3.3): fewer than MIN_USEC_POINTS written
    time dirs cannot establish a plateau and IC2 refuses rather than assume one.
    """
    fails = []
    if len(hist) < MIN_USEC_POINTS:
        fails.append("IC2 plateau: only %d |U_sec| write point(s); at least %d are "
                     "needed to establish a plateau (write cadence is a freeze-time "
                     "decision, §3.3)" % (len(hist), MIN_USEC_POINTS))
        return fails
    vals = [v for _t, v in hist]
    ntail = max(2, int(len(vals) * PLATEAU_TAIL_FRAC))
    tail = vals[-ntail:]
    last = vals[-1]
    # NULL REGIME (§6.3): a converged linear EVM in a duct produces no secondary
    # flow, so |U_sec|_max sits at machine round-off (~1e-14 m/s) and jitters
    # O(100 %) RELATIVE between late writes -- noise, not an unsettled signal.  The
    # pre-registration is explicit that at the null "the plateau is trivially
    # satisfied and the binary reads null".  The history is |U_sec|_max in m/s, so
    # the null ceiling is the binary FLOOR carried into m/s (FLOOR * U_bulk); the
    # relative-movement test applies ONLY to a genuine recovering signal ABOVE it.
    # (A blanket relative test on round-off would spuriously refuse the very
    # baseline model whose null is the thing being explained -- DEFECT E1.)
    if abs(last) < FLOOR * U_BULK:
        return fails
    dev = max(abs(x - last) for x in tail) / abs(last)
    if dev > PLATEAU_RTOL:
        fails.append("IC2 plateau: over the final %d of %d |U_sec| writes the value "
                     "moves %.3e relative, registered ceiling %.0e"
                     % (ntail, len(vals), dev, PLATEAU_RTOL))
    return fails


# ==========================================================================
# Roache.  The monotone branch is the ONLY branch that reaches p / f_ext / GCI.
# (Copied from grade_g2.py's classify/roache -- the pattern the supervisor knows.)
# ==========================================================================
def classify(f_coarse, f_med, f_fine, floor_mode, floor):
    """Returns (label, R, eps21, eps32).  Roache indices: 1=fine, 2=med, 3=coarse."""
    e21 = f_fine - f_med
    e32 = f_med - f_coarse
    fl = floor * abs(f_fine) if floor_mode == "rel" else floor
    small21, small32 = abs(e21) < fl, abs(e32) < fl
    if small21 and small32:
        return "EXACT", None, e21, e32
    if small21 or small32:
        return "STAGNANT", None, e21, e32
    R = e21 / e32
    if R < 0.0:
        return "OSCILLATORY", R, e21, e32
    if R >= 1.0:
        return "DIVERGENT", R, e21, e32
    return "CONVERGING", R, e21, e32


def roache(f_coarse, f_med, f_fine, floor_mode=ROACHE_FLOOR_MODE, floor=ROACHE_FLOOR):
    label, R, e21, e32 = classify(f_coarse, f_med, f_fine, floor_mode, floor)
    out = {"label": label, "R": R, "eps21": e21, "eps32": e32,
           "p": None, "f_ext": None, "gci_pct": None}
    if label != "CONVERGING":
        # standing rule 5: no GCI is computed, let alone printed, off the monotone
        # branch.  This return is the enforcement.
        return out
    if R21 != R32:
        refuse("ROACHE: this comparator is frozen at constant r; r21=%g r32=%g"
               % (R21, R32))
    p = math.log(abs(e32 / e21)) / math.log(R21)
    denom = R21 ** p - 1.0
    if denom <= 0.0:
        refuse("ROACHE: r^p - 1 = %g is not positive; the extrapolation is undefined"
               % denom)
    if f_fine == 0.0:
        refuse("ROACHE: the fine-grid value is exactly zero; a relative GCI is "
               "undefined")
    out.update(p=p, f_ext=f_fine + e21 / denom,
               gci_pct=100.0 * FS * abs(e21 / f_fine) / denom)
    return out


# ==========================================================================
# verdict mapping (§5.2), in rule-1 vocabulary only.
# ==========================================================================
def binary_class(f_fine):
    """BINARY channel (§3.1): does the finest-level metric cross the linear-null
    FLOOR?  NOT Roache-gated -- a qualitative claim (§6.3)."""
    return "linear-null" if f_fine < FLOOR else "recovering"


def model_verdict(binary, res, band=BAND):
    """One verdict per model, faithful to PREREGISTRATION.md §5.2 rows 1-4.

    AMBIGUITY RESOLVED, flagged for the supervisor (§6.1-adjacent): a linear-null
    model (binary below the floor) returns the BASELINE PASS of §5.2 row 1 and is
    NOT subjected to the rule-5 one-way gate, because its quantitative triple is
    machine noise at the null (§6.3) and would spuriously read EXACT/STAGNANT ->
    NOT A RESULT.  The rule-5 gate governs the QUANTITATIVE metric of a RECOVERING
    model in full (§3.3): a non-CONVERGING triple there is NOT A RESULT before any
    band test.  The gate only ever turns PASS/GATE FAIL INTO NOT A RESULT.
    """
    if binary == "linear-null":
        return "PASS"                       # §5.2 row 1: the SST-could-not baseline holds
    if res["label"] != "CONVERGING":        # §5.2 row 4 / rule 5, checked FIRST
        return "NOT A RESULT"
    lo, hi = band
    if lo <= res["f_ext"] <= hi:
        return "PASS"                       # §5.2 row 2: recovers, within the DNS band
    return "GATE FAIL"                       # §5.2 row 3: recovers, misses the DNS band


def say(verdict):
    """No verdict leaves this instrument that is not one of the fixed six (rule 1)."""
    if verdict not in VERDICTS:
        refuse("VOCABULARY: %r is not one of the fixed six verdicts %r. Standing "
               "rule 1 admits no synonym and no hedge." % (verdict, VERDICTS))
    return verdict


# ==========================================================================
# grading
# ==========================================================================
def grade(run_root=RUN_ROOT):
    no_assert_control()
    run_root = Path(run_root)
    if not run_root.is_dir():
        refuse("RUN-ROOT: %s does not exist; there is nothing to grade. (Expected "
               "while LR1 is PENDING_SUPERVISOR_FREEZE and zero-compute; §8(c) "
               "requires all 27 run dirs ABSENT before the freeze.)" % run_root)
    tmp = tempfile.mkdtemp(prefix="lr1grade_")

    print("=" * 78)
    print("LR1 MODEL-FORM LADDER -- square duct AR_1_Ret_360, secondary-velocity "
          "comparator")
    print("  run root : %s" % run_root)
    print("  metric   : |U_sec|_max / U_bulk,  |U_sec| = sqrt(V^2 + W^2) per cell")
    print("  U_bulk   : %.3f m/s   floor : %.1e   DNS band : [%.4f, %.4f] "
          "(DNS %.4f)" % (U_BULK, FLOOR, BAND[0], BAND[1], DNS_USEC_OVER_UBULK))
    print("  r21 = %.4f   r32 = %.4f   Fs = %.2f   (grid triple REUSED from G2)"
          % (R21, R32, FS))
    print("  ALL THRESHOLDS ABOVE ARE DRAFT PENDING-FREEZE (bound at the LR1 freeze "
          "commit by sha256)")
    print("=" * 78)

    # ---- planted controls (rule 3, §6.1), BEFORE any real field is read ----
    print("\n[PLANTED CONTROLS -- rule 3, §6.1, before any real field is read]")
    want, got, base_max, blind_fired = planted_zero_control(tmp)
    print("  Usec   : planted |U_sec|_max = %.6f m/s written to disk and read back "
          "%.6f\n           by the production read_Usec; the UNPLANTED file reads "
          "%.3e, so the\n           reader is not a constant; a 0.0-everywhere reader "
          "was CAUGHT (blind\n           control fired = %r), so a linear-null "
          "model's near-zero is a reading" % (want, got, base_max, blind_fired))
    fa, fb, fc = planted_control_fatal()
    print("  fatal  : a genuine FATAL block reads %r, a fired sigFpe reads %r, a "
          "CLEAN log\n           carrying the `trapFpe:` banner verbatim reads %r -- "
          "a detector, not a constant" % (fa, fb, fc))

    # ---- per-model grading -------------------------------------------------
    print("\n[PER-MODEL GRADE]")
    rows = {}
    infra_all = []
    for name, scale, rsm, rung, klass in MODELS:
        fields = req_fields(scale, rsm)
        channels = req_res(scale)
        print("\n  MODEL %s  [%s, rung %d]  required fields %r"
              % (name, klass, rung, fields))
        blocked, vals, diags = [], {}, {}
        for lvl, ncells, end in LEVELS:
            case = run_root / name / lvl
            if not case.is_dir():
                blocked.append((lvl, ["P0 case dir %s absent" % case]))
                continue
            phys, infra, log = completion(case, end, ncells, fields)
            infra_all += ["%s/%s %s" % (name, lvl, x) for x in infra]
            if phys:
                blocked.append((lvl, phys))
                continue
            icf, diag = iterative_residual(log, channels)
            hist = usec_history(case, ncells)
            icf += iterative_plateau(hist)
            diags[lvl] = diag
            if icf:
                blocked.append((lvl, icf))
                continue
            vals[lvl] = read_Usec(case / str(end) / "U", ncells) / U_BULK
        if blocked:
            v = say("NOT A RESULT")
            rows[name] = (v, None, None)
            print("      VERDICT: %s -- rule 5 step 1: a level not complete or not "
                  "iteratively\n      converged makes the model NOT A RESULT whatever "
                  "any number says. No Roache\n      arithmetic was performed." % v)
            for lvl, reasons in blocked:
                print("        %s REFUSED: %s" % (lvl, "; ".join(reasons)))
            continue
        fc_, fm_, ff_ = vals["L1"], vals["L2"], vals["L3"]
        # BINARY FIRST (DEFECT E2): rule 5 governs the QUANTITATIVE metric of a
        # RECOVERING model only.  A linear-null model's in-plane field is machine
        # noise (§6.3); running Roache on it is meaningless AND fragile -- a noise
        # triple can classify CONVERGING with an exactly-zero fine value and make
        # roache() refuse (exit 2), crashing the whole grade over a model whose
        # verdict does not even use the triple.  So compute the binary, and only
        # run Roache arithmetic when there is a genuine signal to extrapolate.
        binary = binary_class(ff_)
        res = None if binary == "linear-null" else roache(fc_, fm_, ff_)
        v = say(model_verdict(binary, res))
        rows[name] = (v, res, ff_)
        print("      L1 = %.9g   L2 = %.9g   L3 = %.9g   (|U_sec|_max/U_bulk)"
              % (fc_, fm_, ff_))
        print("      binary (finest level vs floor %.1e): %s" % (FLOOR, binary))
        if binary == "linear-null":
            print("      triple: NOT graded -- rule 5 governs the quantitative metric "
                  "of a RECOVERING\n      model only; a linear-null model's in-plane "
                  "field is machine noise (§6.3), so no\n      Roache arithmetic is run "
                  "on it. The baseline prediction (SST-could-not) holds.")
        else:
            print("      triple = %s   R = %s"
                  % (res["label"],
                     "%.6f" % res["R"] if res["R"] is not None else "undefined"))
        if binary != "linear-null":
            if res["label"] == "CONVERGING":
                dev = 100.0 * abs(res["f_ext"] - DNS_USEC_OVER_UBULK) / DNS_USEC_OVER_UBULK
                print("      p = %.6f   f_ext = %.9g   GCI_fine = %.4f %% (Fs=%.2f)   "
                      "f_ext vs DNS %.4f: %.3f %%"
                      % (res["p"], res["f_ext"], res["gci_pct"], FS,
                         DNS_USEC_OVER_UBULK, dev))
            else:
                print("      p, f_ext and GCI are NOT computed: rule 5 forbids quoting "
                      "an order or a\n      GCI when the three values are not monotone.")
        print("      TOPOLOGY (§3.1 M-bin corner-vortex count): %s -- not implemented "
              "in this\n      instrument; the binary's floor-crossing IS computed, its "
              "topology component\n      is not closed here (see module docstring)."
              % say("PENDING"))
        print("      VERDICT: %s" % v)

    # ---- rung 4 (GP): BLOCKED, capability-absent (§1.4) --------------------
    print("\n  RUNG 4 (GP closures): %s -- capability-absent; no GP turbulence model "
          "is built\n  on this box (§1.4). A registered verdict, not a non-result."
          % say("BLOCKED"))

    for x in infra_all:
        print("  INFRASTRUCTURE DEFECT carried into the record (voids nothing, "
              "L-342): %s" % x)

    print("\n[COST CALIBRATION -- owed at completion, standing rule 12]")
    print("  Each solve records wall_s.txt; at rung/case completion the team lands a "
          "row in\n  docs/COST_CALIBRATION.md turning the per-model-class multipliers "
          "(§7) from\n  estimates into measurements. A completion report without it "
          "is incomplete.")
    shutil.rmtree(tmp, ignore_errors=True)
    fails = [n for n, (v, *_r) in rows.items() if v == "GATE FAIL"]
    return 1 if fails else 0


# ==========================================================================
# selftest -- every refusal arm demonstrated to FIRE on a planted mutation,
# and the positive path shown to succeed.  No real solve output is read.
# ==========================================================================
def _must_refuse(label, fn):
    try:
        fn()
    except Refusal as e:
        print("  REFUSED as registered: %s\n      %s"
              % (label, str(e).split("\n")[0][:150]))
        return True
    print("  CONTROL DID NOT FIRE: %s" % label)
    return False


def _synth_case(case, model, scale, rsm, end, ncells, usec_series, res=None,
                bad_res=None):
    """A minimal, complete synthetic run tree, used ONLY by the selftest.

    usec_series maps time -> |U_sec|_max, one written U per time dir; the other
    per-model required fields are written at endTime.  0/U is created FIRST so
    the endTime fields are strictly newer (age guard)."""
    case = Path(case)
    shutil.rmtree(case, ignore_errors=True)
    (case / "0").mkdir(parents=True)
    (case / "0/U").write_text("synthetic age marker\n")
    fields = req_fields(scale, rsm)
    d = case / str(end)
    d.mkdir(parents=True)
    for f in fields:
        if f == "U":
            continue
        (d / f).write_text("synthetic\n")
    # one U per time dir, with the requested |U_sec|_max (corner cell (V,W))
    for t, usec in usec_series.items():
        td = case / str(t)
        td.mkdir(parents=True, exist_ok=True)
        vecs = [(10.0, 0.0, 0.0) for _ in range(ncells)]
        vecs[0] = (10.0, usec, 0.0)      # |U_sec| = usec at the corner
        (td / "U").write_text(_write_U(vecs))
    # log
    resvals = dict(Ux="1e-14", k="1e-9", omega="1e-15", epsilon="1e-15")
    if res:
        resvals.update(res)
    lines = []
    for i in range(1, end + 1):
        lines.append("Time = %d\n" % i)
        lines.append("DILUPBiCGStab:  Solving for Ux, Initial residual = %s, "
                     "Final residual = 1e-16, No Iterations 1\n" % resvals["Ux"])
        lines.append("DILUPBiCGStab:  Solving for Uy, Initial residual = 0.31, "
                     "Final residual = 1e-3, No Iterations 1\n")
        lines.append("DILUPBiCGStab:  Solving for Uz, Initial residual = 0.42, "
                     "Final residual = 1e-3, No Iterations 1\n")
        lines.append("GAMG:  Solving for p, Initial residual = 0.19, "
                     "Final residual = 1e-3, No Iterations 3\n")
        lines.append("DILUPBiCGStab:  Solving for %s, Initial residual = %s, "
                     "Final residual = 1e-16, No Iterations 1\n"
                     % (scale, resvals[scale]))
        lines.append("DILUPBiCGStab:  Solving for k, Initial residual = %s, "
                     "Final residual = 1e-11, No Iterations 1\n" % resvals["k"])
        lines.append("ExecutionTime = %d s  ClockTime = %d s\n\n" % (i, i))
    lines.append("End\n")
    (case / "log.run").write_text("".join(lines))
    (case / "rc.txt").write_text("0\n")
    (case / "wall_s.txt").write_text("1\n")
    (case / "log.checkMesh").write_text("Mesh OK.\n")
    (case / "mem_time.txt").write_text("\tMaximum resident set size (kbytes): 1\n")
    return case


def selftest():
    ok = True
    print("LR1 comparator selftest -- every refusal arm on a planted mutation")
    planted, own = no_assert_control()
    print("  L-332: counter saw %d planted assert, this module holds %d"
          % (planted, own))
    ok &= _must_refuse("a source text holding an ast.Assert node",
                       lambda: (count_asserts("assert True\n") == 1
                                and refuse("planted assert present")))
    tmp = Path(tempfile.mkdtemp(prefix="lr1self_"))

    # ---- planted-zero control, all four arms ------------------------------
    print("\n[planted-zero control -- §6.1]")
    want, got, base_max, blind_fired = planted_zero_control(tmp)
    if abs(got - want) < PLANT_RTOL and base_max < want and blind_fired:
        print("  positive path: read_Usec recovered the planted %.6f (base reads "
              "%.3e), blind\n  reader CAUGHT" % (want, base_max))
    else:
        print("  FAIL: positive path did not behave"); ok = False
    # arm: reader cannot see the plant
    ok &= _must_refuse("a reader that returns the wrong |U_sec|_max (cannot see plant)",
                       lambda: _recovery_check(lambda p, n: 0.123, tmp / "planted_U",
                                               CONTROL_NCELLS, PLANT_USEC, "NEG reader"))
    # arm: substitution changed no bytes (base == planted)
    def _no_byte_change():
        base = [(10.0, 0.0, 0.0) for _ in range(CONTROL_NCELLS)]
        t = _write_U(base)
        if t == t:                                        # base == "planted" (no change)
            refuse("PLANT Usec: the corner substitution changed no bytes")
    ok &= _must_refuse("a plant that changed no bytes", _no_byte_change)
    # arm: inverse -- a constant reader that returns the plant on the unplanted file
    def _constant_reader():
        bp = tmp / "base_U"
        base_max = (lambda p, n: PLANT_USEC)(bp, CONTROL_NCELLS)
        if abs(base_max - PLANT_USEC) <= PLANT_RTOL * abs(PLANT_USEC):
            refuse("PLANT Usec inverse: the reader returns the plant on the UNPLANTED "
                   "file; it is a constant, not a reader")
    ok &= _must_refuse("a constant reader (inverse control)", _constant_reader)
    # arm: blind reader NOT caught -> the recovery check would be a no-op
    ok &= _must_refuse("a blind (0.0-everywhere) reader against the planted field",
                       lambda: _recovery_check(lambda p, n: 0.0, tmp / "planted_U",
                                               CONTROL_NCELLS, PLANT_USEC, "BLIND"))
    # arm: reader length check
    def _wrong_count():
        vecs = [(10.0, 0.0, 0.0) for _ in range(CONTROL_NCELLS - 1)]
        p = tmp / "short_U"; p.write_text(_write_U(vecs))
        read_Usec(p, CONTROL_NCELLS)
    ok &= _must_refuse("a U field with the wrong cell count", _wrong_count)

    # ---- fatal reader, both directions ------------------------------------
    print("\n[fatal reader -- both directions, rule 3]")
    fa, fb, fc = planted_control_fatal()
    print("  FATAL block -> %r, fired sigFpe -> %r, clean `trapFpe:` banner -> %r"
          % (fa, fb, fc))

    # ---- Roache classification / gating -----------------------------------
    print("\n[Roache classification and the no-GCI-off-monotone rule]")
    for want_lbl, fc_, fm_, ff_ in (("CONVERGING", 10.0, 6.0, 4.0),
                                    ("DIVERGENT", 4.0, 6.0, 10.0),
                                    ("OSCILLATORY", 10.0, 4.0, 6.0)):
        got_lbl = classify(fc_, fm_, ff_, "rel", 1e-9)[0]
        if got_lbl != want_lbl:
            print("  FAIL: (%g,%g,%g) -> %s, expected %s"
                  % (fc_, fm_, ff_, got_lbl, want_lbl)); ok = False
        else:
            print("  (%g, %g, %g) -> %s" % (fc_, fm_, ff_, got_lbl))
    if classify(1.0, 1.0, 1.0, "rel", 1e-3)[0] != "EXACT":
        print("  FAIL: three equal values are not EXACT"); ok = False
    else:
        print("  three equal values -> EXACT")
    if classify(2.0, 1.0, 1.0, "rel", 1e-3)[0] != "STAGNANT":
        print("  FAIL: one difference below the floor is not STAGNANT"); ok = False
    else:
        print("  one difference below the floor -> STAGNANT")
    for lbl, fc_, fm_, ff_ in (("DIVERGENT", 4.0, 6.0, 10.0),
                               ("OSCILLATORY", 10.0, 4.0, 6.0),
                               ("EXACT", 1.0, 1.0, 1.0),
                               ("STAGNANT", 2.0, 1.0, 1.0)):
        r = roache(fc_, fm_, ff_, "rel", 1e-3)
        if r["gci_pct"] is not None or r["p"] is not None or r["f_ext"] is not None:
            print("  FAIL: %s produced p/f_ext/GCI" % lbl); ok = False
    print("  DIVERGENT/OSCILLATORY/EXACT/STAGNANT all return with p, f_ext and GCI "
          "still None")
    r = roache(10.0, 6.0, 4.0, "rel", 1e-9)
    if abs(r["p"] - math.log(2.0) / math.log(2.0)) > 1e-12:
        print("  FAIL: p = %.12g, closed form 1.0" % r["p"]); ok = False
    else:
        print("  CONVERGING: p = %.6f matches the closed form at r = 2" % r["p"])

    # ---- verdict mapping (§5.2), synthetic triples ------------------------
    print("\n[verdict mapping -- §5.2, synthetic triples on |U_sec|_max/U_bulk]")
    lo, hi = BAND
    mid = 0.5 * (lo + hi)                     # inside the band, well above the floor
    above = hi + 0.01                         # above the band
    null = 1e-14                              # linear-null, below the floor
    mapping_tests = [
        # name,                       (L1, L2, L3),                   expect
        ("linear-null (below floor)", (null * 0.9, null * 0.95, null), "PASS"),
        ("recovering, CONVERGING, in band",
         (mid * 1.4, mid * 1.15, mid), "PASS"),
        ("recovering, CONVERGING, out of band",
         (above * 1.4, above * 1.15, above), "GATE FAIL"),
        ("recovering, DIVERGENT triple",
         (mid * 0.8, mid * 0.9, mid), "NOT A RESULT"),
        ("recovering, OSCILLATORY triple",
         (mid * 1.2, mid * 0.9, mid), "NOT A RESULT"),
        ("recovering, EXACT triple",
         (mid, mid, mid), "NOT A RESULT"),
    ]
    seen_labels = set()
    for nm, (a, b, c), expect in mapping_tests:
        res = roache(a, b, c)
        binary = binary_class(c)
        v = say(model_verdict(binary, res))
        seen_labels.add(res["label"])
        good = v == expect
        ok &= good
        fext = ("%.5f" % res["f_ext"]) if res["f_ext"] is not None else "n/a"
        print("  %s %-38s binary=%-11s triple=%-11s f_ext=%s -> %s (expected %s)"
              % ("ok " if good else "BAD", nm, binary, res["label"], fext, v, expect))
    need = {"CONVERGING", "DIVERGENT", "OSCILLATORY", "EXACT"}
    if not need <= seen_labels:
        print("  BAD: triples exercised %r, missing %r"
              % (sorted(seen_labels), sorted(need - seen_labels))); ok = False
    # the one-way gate: a CONVERGING PASS is turned INTO NOT A RESULT only via the
    # triple, never the reverse -- a not-CONVERGING triple can never yield PASS.
    if model_verdict("recovering", roache(mid, mid, mid)) != "NOT A RESULT":
        print("  BAD: an EXACT recovering triple did not yield NOT A RESULT"); ok = False
    else:
        print("  one-way gate: a not-CONVERGING recovering triple is NOT A RESULT, "
              "never PASS")

    # ---- verdict vocabulary -----------------------------------------------
    print("\n[verdict vocabulary -- rule 1]")
    ok &= _must_refuse("a synonym for a verdict", lambda: say("roughly converged"))
    ok &= _must_refuse("a hedged verdict", lambda: say("mostly PASS"))
    ok &= _must_refuse("a lower-case verdict", lambda: say("pass"))
    for v in VERDICTS:
        if say(v) != v:
            print("  FAIL: %r was not passed through" % v); ok = False
    print("  all six fixed verdicts pass through unchanged; synonym/hedge/lowercase "
          "REFUSED")

    # ---- strict completion + age guard, per-model, mutated ----------------
    print("\n[strict completion + age guard -- §6.2, per-model, mutated]")
    # a clean linear (omega) case
    case = tmp / "kOmegaSST_L1"
    _synth_case(case, "kOmegaSST", "omega", False, 10, 4,
                {8: 1e-14, 9: 1e-14, 10: 1e-14})
    fields = req_fields("omega", False)
    phys, infra, log = completion(case, 10, 4, fields)
    if phys:
        print("  FAIL: a clean synthetic omega run was refused: %r" % phys); ok = False
    else:
        print("  a clean synthetic omega run passes all PHYSICS clauses; infra "
              "recorded: %r" % infra)
    # a clean RSM case needs R and epsilon present
    rcase = tmp / "LRR_L1"
    _synth_case(rcase, "LRR", "epsilon", True, 10, 4, {8: 1e-14, 9: 1e-14, 10: 1e-14})
    rphys, _ri, _rl = completion(rcase, 10, 4, req_fields("epsilon", True))
    if rphys:
        print("  FAIL: a clean synthetic RSM run was refused: %r" % rphys); ok = False
    else:
        print("  a clean synthetic RSM run (U p k epsilon nut R) passes")
    # P5: an RSM missing its R field
    (rcase / "10" / "R").unlink()
    if not any(x.startswith("P5") for x in completion(rcase, 10, 4,
                                                       req_fields("epsilon", True))[0]):
        print("  FAIL: a missing RSM stress field R was not caught"); ok = False
    else:
        print("  RSM missing R                       CAUGHT (P5, per-model field set)")
    # P1 rc
    (case / "rc.txt").write_text("1\n")
    if not any(x.startswith("P1") for x in completion(case, 10, 4, fields)[0]):
        print("  FAIL: rc = 1 not caught"); ok = False
    else:
        print("  rc = 1                              CAUGHT (P1)")
    (case / "rc.txt").write_text("0\n")
    # P2 End
    txt = (case / "log.run").read_text()
    (case / "log.run").write_text(txt.replace("\nEnd\n", "\n"))
    if not any(x.startswith("P2") for x in completion(case, 10, 4, fields)[0]):
        print("  FAIL: a missing End line not caught"); ok = False
    else:
        print("  no End line                         CAUGHT (P2)")
    # P7 ExecutionTime hard equality
    (case / "log.run").write_text(txt.replace("ExecutionTime = 1 s", "", 1))
    if not any(x.startswith("P7") for x in completion(case, 10, 4, fields)[0]):
        print("  FAIL: ExecutionTime count 9 vs endTime 10 not caught"); ok = False
    else:
        print("  ExecutionTime count 9 vs endTime 10 CAUGHT (P7, hard equality)")
    (case / "log.run").write_text(txt)
    # P6 age guard
    os.utime(case / "0/U", None)
    if not any(x.startswith("P6") for x in completion(case, 10, 4, fields)[0]):
        print("  FAIL: an age marker newer than the answer not caught"); ok = False
    else:
        print("  0/U touched AFTER the fields         CAUGHT (P6 age guard)")

    # ---- iterative convergence --------------------------------------------
    print("\n[iterative convergence -- §6.3]")
    c2 = tmp / "kOmegaSST_L2"
    _synth_case(c2, "kOmegaSST", "omega", False, 10, 4,
                {8: 1.00e-14, 9: 1.00e-14, 10: 1.00e-14})
    log = parse_log(c2 / "log.run")
    icf, diag = iterative_residual(log, req_res("omega"))
    icf += iterative_plateau(usec_history(c2, 4))
    if icf:
        print("  FAIL: a clean synthetic case was refused: %r" % icf); ok = False
    else:
        print("  a clean case passes IC1 (Ux/k/omega) and IC2 (|U_sec| plateau); "
              "p/Uy/Uz diagnostic %r"
              % {k: ("%.2g" % v if v is not None else None) for k, v in diag.items()})
    # IC1: a bad k residual
    bad = parse_log_text_mut(c2, "Solving for k, Initial residual = 1e-9",
                             "Solving for k, Initial residual = 1")
    if not any(x.startswith("IC1") for x in iterative_residual(bad, req_res("omega"))[0]):
        print("  FAIL: a k residual of 1 not caught"); ok = False
    else:
        print("  final k residual 1.0                CAUGHT (IC1)")
    # IC2: a |U_sec| wobble in the tail of a genuine SIGNAL (above FLOOR*U_bulk ~=
    # 0.085 m/s, near the DNS peak ~1.75 m/s) -- the relative test applies only in
    # the signal regime, so the wobble must sit there to be gated (post-E1-fix).
    c3 = tmp / "kOmegaSST_L3"
    _synth_case(c3, "kOmegaSST", "omega", False, 10, 4,
                {8: 1.750, 9: 1.785, 10: 1.750})     # 2 % move in the tail, a real signal
    if not any(x.startswith("IC2") for x in iterative_plateau(usec_history(c3, 4))):
        print("  FAIL: a signal-regime |U_sec| tail wobble not caught"); ok = False
    else:
        print("  |U_sec| wobbling 2 %% in the tail    CAUGHT (IC2 plateau, signal regime)")
    # IC2: too few write points (fires regardless of regime, before the regime test)
    c4 = tmp / "kOmegaSST_L4"
    _synth_case(c4, "kOmegaSST", "omega", False, 10, 4, {10: 1.750})
    if not any(x.startswith("IC2") for x in iterative_plateau(usec_history(c4, 4))):
        print("  FAIL: a single |U_sec| write point not caught"); ok = False
    else:
        print("  only 1 |U_sec| write point          CAUGHT (IC2, cadence)")

    # ---- DEFECT E1 + E2: the linear-null baseline through the FULL grade() path
    print("\n[linear-null baseline through the FULL grade() path -- E1 + E2]")
    # E1 (unit): a round-off-jitter null series, O(100 %) relative and ALL below the
    # FLOOR, now PASSES the plateau trivially.  Pre-fix this returned an IC2 failure
    # and BLOCKED the baseline model to NOT A RESULT (verified against pre-fix code).
    null_hist = [(2, 2e-15), (5, 5e-15), (8, 1.5e-15)]
    if iterative_plateau(null_hist):
        print("  FAIL(E1): a linear-null round-off series was refused by IC2"); ok = False
    else:
        print("  E1: null round-off jitter (2e-15, 5e-15, 1.5e-15 m/s) PASSES IC2 "
              "trivially (null regime)")
    # E2 (the hazard is real): roache() DOES refuse on an exact-zero-fine CONVERGING
    # noise triple -- so it MUST NOT be called on a linear-null model...
    ok &= _must_refuse("roache() on an exact-zero-fine CONVERGING noise triple "
                       "(the crash the fix avoids by not calling it)",
                       lambda: roache(3e-15 / U_BULK, 1e-15 / U_BULK, 0.0))
    # ...and the fix is exactly that: binary_class(0.0)=='linear-null' short-circuits
    # to a baseline PASS with res=None, so roache is never reached on noise.
    if binary_class(0.0) == "linear-null" and model_verdict("linear-null", None) == "PASS":
        print("  E2: binary_class(0.0)='linear-null' -> model_verdict PASS with "
              "res=None; roache NOT called on noise")
    else:
        print("  FAIL(E2): linear-null did not short-circuit roache"); ok = False
    # FULL PATH: the REAL grade() end-to-end on a run root whose kOmegaSST triple is
    # linear-null with an exact-zero fine level -- the case that, once E1 is lifted,
    # reaches roache and crashes (exit 2) WITHOUT the E2 fix.  It must now return 0
    # with kOmegaSST reading the baseline PASS (LEVELS narrowed to a small endTime for
    # a small synthetic log; the grade_g2._blind_fatal global-swap precedent).
    rc_full, out_full = _grade_linear_null_full_path(tmp)
    if rc_full == 0 and "linear-null" in out_full and "VERDICT: PASS" in out_full:
        print("  FULL PATH: grade() returned 0 (no crash), kOmegaSST binary=linear-null "
              "-> VERDICT: PASS end-to-end")
    else:
        print("  FAIL(E1+E2 full path): rc=%r, linear-null=%r, PASS=%r"
              % (rc_full, "linear-null" in out_full, "VERDICT: PASS" in out_full))
        ok = False

    # ---- run root ---------------------------------------------------------
    print("\n[run root]")
    ok &= _must_refuse("an absent run root", lambda: grade(tmp / "nope"))

    shutil.rmtree(tmp, ignore_errors=True)
    print("\nSELFTEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def _grade_linear_null_full_path(tmp):
    """Drive the REAL grade() on a linear-null kOmegaSST triple (E1 + E2).

    LEVELS is temporarily narrowed to a small endTime/ncells so the synthetic
    solver log is small -- the grade_g2._blind_fatal global-swap precedent -- while
    grade()'s own code (completion, iterative, the binary-first roache skip,
    model_verdict, the vocabulary checker) runs unmodified.  The fine level's
    |U_sec|_max is EXACTLY zero and the triple classifies CONVERGING, so without
    the E2 fix grade() would call roache() and refuse (exit 2) once the E1 fix lets
    the null write series pass the plateau.  Returns (rc, captured_stdout)."""
    global LEVELS
    saved = LEVELS
    LEVELS = (("L1", 4, 6), ("L2", 4, 6), ("L3", 4, 6))
    try:
        root = Path(tmp) / "lnull_root"
        levelseries = {
            "L1": {2: 2e-15, 4: 5e-15, 6: 3e-15},   # endTime(6)=3e-15 -> triple L1
            "L2": {2: 2e-15, 4: 5e-15, 6: 1e-15},   # endTime(6)=1e-15 -> triple L2
            "L3": {2: 2e-15, 4: 5e-15, 6: 0.0},     # endTime(6)=0.0   -> triple L3, EXACT zero
        }
        for lvl, series in levelseries.items():
            _synth_case(root / "kOmegaSST" / lvl, "kOmegaSST", "omega", False,
                        6, 4, series)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = grade(root)
        except Refusal as e:
            return -2, "REFUSED (grade crashed on linear-null noise): %s" % e
        return rc, buf.getvalue()
    finally:
        LEVELS = saved


def parse_log_text_mut(case, old, new):
    """Read a synthetic log, substitute, re-parse -- a selftest helper."""
    p = Path(case) / "log.run"
    return parse_log_from_text(p.read_text().replace(old, new))


def parse_log_from_text(text):
    """parse_log on an in-memory string (selftest helper; writes to a temp file)."""
    with tempfile.NamedTemporaryFile("w", suffix=".run", delete=False) as fh:
        fh.write(text)
        name = fh.name
    try:
        return parse_log(name)
    finally:
        os.unlink(name)


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = RUN_ROOT
    for a in argv:
        if not a.startswith("-"):
            root = Path(a)
    return grade(root)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        sys.exit(2)
