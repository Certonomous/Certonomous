"""G1b comparator: the SUCCESSOR to G1, grading the SAME completed run root
with the SAME frozen registry and a REPAIRED fatal clause.

G1 is graded NOT A RESULT.  That verdict is permanent and is not revised here:
grade_g1.py is frozen and post-compute (standing rules 2 and 6) and is not
edited.  This file exists because G1's fatal clause was very nearly a constant
(see the FATAL DETECTION block below for the measured figures), and a repair to
a frozen comparator can only land in a re-frozen, re-registered successor.

Strict completion, planted-disk controls, refinement-family control, Roache
triple classification and GCI -- every band, threshold, level and ceiling copied
verbatim from G1.  Nothing was widened.

It reads only from disk, launches nothing, and touches no git index.

Standing-rule compliance carried here:
  rule 3  planted zero -- FOUR controls, each of which WRITES A REAL FILE,
          reads it back through the SAME reader used on the real data, and
          sys.exit(2)s if the reader cannot see the plant.  An in-memory plant
          does not satisfy this rule and none is used.  The fourth control is
          new in G1b and is on the FATAL CHANNEL, in BOTH directions: a
          fatal detector never shown able to return NOT-fatal is a constant,
          not a reader, and that is precisely the defect being repaired.
  read-only
          this comparator never writes, touches or chmods anything under
          RUN_ROOT.  Every plant is written into a tempfile.TemporaryDirectory.
          main() takes a stat digest of the whole run root before and after the
          grading pass and refuses if it changed.
  rule 4  strict completion + age guard, all-or-nothing, refusing rather than
          degrading.
  rule 5  Roache gating -- a non-CONVERGING triple is NOT A RESULT whatever the
          value; GCI at Fs = 1.25 is computed and printed ONLY inside the
          CONVERGING branch, which is exactly the monotone branch.
  L-342   every completion clause is labelled PHYSICS or INFRASTRUCTURE; an
          infrastructure defect is recorded and named, and cannot by itself
          void the physics.
  L-332   no `assert` carries a refusal; the module refuses if its own AST holds
          one; --selftest is run under python3 -O with every refusal still firing.
"""

import ast
import hashlib
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

RUN_ROOT = Path("/home/ubuntu/closure-data/g1")

# ---- FROZEN REGISTRY (PREREGISTRATION.md sections 2, 4, 5) ----------------
# coarse -> fine.  Roache indices: 1 = finest = L3, 2 = L2, 3 = coarsest = L1.
LEVELS = (
    ("L1", 3840, 20000),
    ("L2", 15360, 30000),
    ("L3", 61440, 60000),
)
D_SPATIAL = 2               # one cell in z between `empty` patches: a 2D problem
R21 = 2.0                   # h(L2)/h(L3) = (61440/15360)^(1/2)
R32 = 2.0                   # h(L1)/h(L2) = (15360/3840)^(1/2)
FS = 1.25                   # Roache factor of safety, three-grid GCI
DOMAIN_VOLUME = 5.0826      # m^3, checkMesh "Total volume"; tol below is loose
DOMAIN_VOLUME_RTOL = 1e-4

REQ_FIELDS = ("U", "p", "k", "omega", "nut")
AGE_MARKER = "0/U"

# iterative convergence, per level, ALL must hold
RES_MAX = {"Ux": 1e-5, "Uy": 1e-5, "Uz": 1e-5, "k": 1e-5, "omega": 1e-5, "p": 1e-4}
RES_REQUIRED = ("Ux", "Uy", "p", "k", "omega")
PLATEAU_TAIL_FRAC = 0.10
PLATEAU_RTOL = 1e-4
DISK_VS_LOG_RTOL = 1e-9

# reattachment functional
X_REF_ATTACHED = 6.5        # physical x, deep in the attached flat floor
X_SEARCH_MIN = 0.5          # physical x, downstream of the crest
TAU_FLOOR = 1e-8

# functional registry: key -> (label, unit, p_lo, p_hi, gci_max_pct, floor_mode, floor)
FUNCTIONALS = (
    ("gradP", "PRIMARY  mean streamwise momentum source", "m/s2",
     1.0, 3.0, 5.0, "rel", 1e-4),
    ("Kint", "SECONDARY-A  volume-integrated k", "m5/s2",
     0.5, 3.0, 10.0, "rel", 1e-4),
    ("xr", "SECONDARY-B  lower-wall reattachment length", "h",
     0.5, 3.0, 10.0, "abs", 1e-3),
)

# planted-control constants
PLANT_GRADP = 1.234567e-03
PLANT_K = 9.876543e+02
PLANT_KUNIFORM = 2.0
PLANT_XR = 4.2345

VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")
TIME_DIR = re.compile(r"^[0-9]+(\.[0-9]*)?([eE][+-]?[0-9]+)?$")


class Refusal(Exception):
    """A condition that must stop this instrument under ANY interpreter flag."""


def refuse(msg):
    raise Refusal(msg)


# --------------------------------------------------------------------------
# L-332 control
# --------------------------------------------------------------------------
def count_asserts(source_text):
    return sum(1 for n in ast.walk(ast.parse(source_text)) if isinstance(n, ast.Assert))


def no_assert_control():
    planted = count_asserts("def f(x):\n    assert x, 'planted'\n    return x\n")
    if planted != 1:
        refuse("AST-CONTROL: the counter returned %d on a snippet with exactly one "
               "assert; its zero here would be a blind spot, not a reading." % planted)
    own = count_asserts(Path(__file__).read_text())
    if own != 0:
        refuse("AST-CONTROL: this module holds %d ast.Assert node(s); python3 -O "
               "deletes every one (L-332)." % own)
    return planted, own


# --------------------------------------------------------------------------
# OpenFOAM ASCII readers.  These are THE readers the planted controls exercise.
# --------------------------------------------------------------------------
NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _skip_ws(t, i):
    while i < len(t):
        if t[i].isspace():
            i += 1
        elif t.startswith("//", i):
            i = t.find("\n", i)
            if i < 0:
                return len(t)
        elif t.startswith("/*", i):
            j = t.find("*/", i)
            i = len(t) if j < 0 else j + 2
        else:
            return i
    return i


def _entry_after(text, keyword, start=0):
    """Return (body, end_index) of `keyword <body>;` with paren nesting honoured."""
    m = re.compile(r"(?m)^\s*" + re.escape(keyword) + r"\b").search(text, start)
    if m is None:
        return None, -1
    i = _skip_ws(text, m.end())
    depth = 0
    j = i
    while j < len(text):
        c = text[j]
        if c in "({":
            depth += 1
        elif c in ")}":
            depth -= 1
        elif c == ";" and depth == 0:
            return text[i:j], j
        j += 1
    return None, -1


def _floats(s):
    return [float(x) for x in NUM.findall(s)]


def read_field_list(path, keyword="internalField", ncomp=1, patch=None):
    """Read an OpenFOAM ASCII field entry as a flat list of floats.

    Handles `uniform <v>` and `nonuniform List<...> N ( ... )`.  With `patch`
    set, reads boundaryField/<patch>/value instead.
    """
    p = Path(path)
    if not p.is_file():
        refuse("READER: %s does not exist" % p)
    text = p.read_text(errors="replace")
    if patch is not None:
        bi = text.find("boundaryField")
        if bi < 0:
            refuse("READER: %s has no boundaryField" % p)
        m = re.compile(r"(?m)^\s*" + re.escape(patch) + r"\s*$").search(text, bi)
        if m is None:
            refuse("READER: %s has no boundary patch %r" % (p, patch))
        i = _skip_ws(text, m.end())
        if i >= len(text) or text[i] != "{":
            refuse("READER: patch %r in %s is not followed by a block" % (patch, p))
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        text = text[i:j]
        keyword = "value"
    body, _ = _entry_after(text, keyword)
    if body is None:
        refuse("READER: %s has no `%s ... ;` entry" % (p, keyword))
    body = body.strip()
    if body.startswith("uniform"):
        vals = _floats(body[len("uniform"):])
        if len(vals) != ncomp:
            refuse("READER: uniform entry in %s gave %d components, expected %d"
                   % (p, len(vals), ncomp))
        return ("uniform", vals)
    if "nonuniform" not in body:
        refuse("READER: %s `%s` is neither uniform nor nonuniform: %r"
               % (p, keyword, body[:60]))
    op = body.find("(")
    cl = body.rfind(")")
    if op < 0 or cl < 0 or cl < op:
        refuse("READER: %s `%s` has no parenthesised list" % (p, keyword))
    vals = _floats(body[op + 1:cl])
    if ncomp > 1:
        if len(vals) % ncomp:
            refuse("READER: %s list length %d is not a multiple of %d"
                   % (p, len(vals), ncomp))
        return ("list", [vals[i:i + ncomp] for i in range(0, len(vals), ncomp)])
    return ("list", vals)


def read_scalar_internal(path, ncells):
    kind, v = read_field_list(path, "internalField", 1)
    if kind == "uniform":
        return [v[0]] * ncells
    if len(v) != ncells:
        refuse("READER: %s internalField holds %d values, mesh has %d cells"
               % (path, len(v), ncells))
    return v


def read_gradP_disk(path):
    p = Path(path)
    if not p.is_file():
        refuse("READER: %s does not exist; the primary functional has no artifact" % p)
    m = re.search(r"(?m)^\s*gradient\s+(" + NUM.pattern + r")\s*;", p.read_text())
    if m is None:
        refuse("READER: %s holds no `gradient <v>;` entry" % p)
    return float(m.group(1))


# --------------------------------------------------------------------------
# log parsing
# --------------------------------------------------------------------------
RE_TIME = re.compile(r"(?m)^Time = (\S+)\s*$")
RE_RES = re.compile(r"Solving for (\w+), Initial residual = (" + NUM.pattern + r")")
RE_GRADP = re.compile(r"pressure gradient = (" + NUM.pattern + r")")
RE_EXEC = re.compile(r"(?m)^ExecutionTime = ")

# --------------------------------------------------------------------------
# FATAL DETECTION -- the one clause repaired in this successor.
#
# G1's frozen clause read, verbatim:
#     bool(re.search(r"FOAM FATAL|Floating point exception|signal", text))
# and OpenFOAM writes, at line 18 of EVERY log it produces:
#     trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).
# That is the solver ANNOUNCING that FPE trapping is ENABLED -- a safety notice
# emitted on a healthy start, not a failure.  The substring "Floating point
# exception" matches it, so the clause fired on every level of a run that had
# completed cleanly, and G1 graded NOT A RESULT on a banner.
#
# MEASURED (closure-supervisor triage, 2026-08-27, with an instrument that
# grades nothing -- no functional, no order, no GCI, no verdict), over 70
# `log.run` files across three families:
#     the G1 clause FIRED on                                    63 of 70
#     of those 63, carry a clean `End` line                     57
#     of those 63, EVERY hit is the trapFpe banner              59
# It is not a fatal detector.  It is very nearly a constant.
#
# The repaired clause below matches only evidence of an ACTUAL failure:
#   FOAM FATAL ERROR / FOAM FATAL IO ERROR -- OpenFOAM's own fatal banners;
#   sigFpe::sigHandler / sigSegv::sigHandler -- a signal handler that actually
#       FIRED, as opposed to one that was merely installed;
#   Foam::error::printStack -- a stack trace was printed;
#   a line that BEGINS with "Floating point exception" or "Segmentation fault"
#       -- the shell's own death message.  The trapFpe banner line does not
#       begin with either word, so the ^ anchor is what separates the two.
# It deliberately does NOT match "trapFpe:", "trapping enabled", or the bare
# word "signal" (which appears in ordinary prose, e.g. "signalling").
# Both directions of this are enforced at run time by planted_control_fatal().
# --------------------------------------------------------------------------
TRAPFPE_BANNER = ("trapFpe: Floating point exception trapping enabled "
                  "(FOAM_SIGFPE).")
RE_TRAPFPE_BANNER = re.compile(r"trapFpe:|trapping enabled")
# The G1 clause, transcribed verbatim.  It is NEVER used to gate anything here.
# It is kept solely so this comparator can COUNT what it would have matched and
# carry that count into the record as INFRASTRUCTURE evidence of the defect.
RE_G1_FATAL_CLAUSE = re.compile(r"FOAM FATAL|Floating point exception|signal")
RE_FATAL = re.compile(
    r"FOAM FATAL ERROR"
    r"|FOAM FATAL IO ERROR"
    r"|sigFpe::sigHandler"
    r"|sigSegv::sigHandler"
    r"|Foam::error::printStack"
    r"|^Floating point exception"
    r"|^Segmentation fault",
    re.M)


def parse_log(path):
    p = Path(path)
    if not p.is_file():
        refuse("LOG: %s does not exist" % p)
    text = p.read_text(errors="replace")
    legacy = [ln for ln in text.split("\n") if RE_G1_FATAL_CLAUSE.search(ln)]
    banner = [ln for ln in legacy if RE_TRAPFPE_BANNER.search(ln)]
    out = {
        "exec_count": len(RE_EXEC.findall(text)),
        "end": bool(re.search(r"(?m)^End\s*$", text)),
        # REPAIRED IN G1b.  See the FATAL DETECTION block above.
        "fatal": bool(RE_FATAL.search(text)),
        "fatal_hits": RE_FATAL.findall(text),
        # INFRASTRUCTURE ONLY -- these two counts gate nothing, ever.
        "legacy_hits": len(legacy),
        "banner_hits": len(banner),
        "gradP_hist": [float(x) for x in RE_GRADP.findall(text)],
        "times": RE_TIME.findall(text),
    }
    blocks = list(RE_TIME.finditer(text))
    if not blocks:
        refuse("LOG: %s holds no `Time = ` block" % p)
    tail = text[blocks[-1].start():]
    final = {}
    for name, val in RE_RES.findall(tail):
        final.setdefault(name, float(val))   # first solve of the field wins
    out["final_res"] = final
    return out


# --------------------------------------------------------------------------
# functionals
# --------------------------------------------------------------------------
def f_gradP(case, end):
    return read_gradP_disk(Path(case) / str(end) / "uniform/momentumSourceProperties")


def f_Kint(case, end, ncells):
    d = Path(case) / str(end)
    k = read_scalar_internal(d / "k", ncells)
    v = read_scalar_internal(d / "V", ncells)
    if len(k) != len(v):
        refuse("Kint: k has %d values, V has %d" % (len(k), len(v)))
    tot = sum(v)
    if abs(tot - DOMAIN_VOLUME) > DOMAIN_VOLUME_RTOL * DOMAIN_VOLUME:
        refuse("Kint: sum(V) = %.9g does not match the registered domain volume "
               "%.6g within %g relative; the volume field is not this mesh's."
               % (tot, DOMAIN_VOLUME, DOMAIN_VOLUME_RTOL))
    return sum(ki * vi for ki, vi in zip(k, v))


def reattachment(tau_path, c_path, patch="bottomWall"):
    """First negative->positive tau_wx crossing at x >= X_SEARCH_MIN, as a
    PHYSICAL x found by linear interpolation between two face centres.  The
    'attached' sign is taken from the flow itself at x = X_REF_ATTACHED, so the
    functional does not depend on OpenFOAM's wall-shear sign convention.
    Returns (x_r, n_crossings)."""
    kind_t, tau = read_field_list(tau_path, ncomp=3, patch=patch)
    kind_c, cc = read_field_list(c_path, ncomp=3, patch=patch)
    if kind_t == "uniform" or kind_c == "uniform":
        refuse("xr: a uniform wall-shear or face-centre list cannot locate a crossing")
    if len(tau) != len(cc):
        refuse("xr: %d wall-shear faces vs %d face centres" % (len(tau), len(cc)))
    pts = sorted(zip((c[0] for c in cc), (t[0] for t in tau)))
    xs = [a for a, _ in pts]
    ts = [b for _, b in pts]
    iref = min(range(len(xs)), key=lambda i: abs(xs[i] - X_REF_ATTACHED))
    if abs(ts[iref]) < TAU_FLOOR:
        refuse("xr: |tau_wx| at the reference station x=%.3f is %.3g, below the "
               "floor %g; the attached sign cannot be established."
               % (xs[iref], ts[iref], TAU_FLOOR))
    s = 1.0 if ts[iref] > 0 else -1.0
    xr, n = None, 0
    for i in range(len(xs) - 1):
        if xs[i] < X_SEARCH_MIN:
            continue
        a, b = s * ts[i], s * ts[i + 1]
        if a <= 0.0 < b:
            n += 1
            if xr is None:
                xr = xs[i] + (xs[i + 1] - xs[i]) * (0.0 - a) / (b - a)
    if xr is None:
        refuse("xr: no negative-to-positive tau_wx crossing at x >= %.3f; there is "
               "no reattachment point to report." % X_SEARCH_MIN)
    return xr, n


# --------------------------------------------------------------------------
# PLANTED-DISK CONTROLS.  Each writes a real file and reads it back through the
# same reader used on the real data.  Rule 3.
# --------------------------------------------------------------------------
def planted_control_gradP(real_path, tmp):
    src = Path(real_path)
    dst = Path(tmp) / "momentumSourceProperties"
    txt = src.read_text()
    planted = re.sub(r"(?m)^(\s*gradient\s+)" + NUM.pattern + r"(\s*;)",
                     r"\g<1>%.9e\g<2>" % PLANT_GRADP, txt)
    if planted == txt:
        refuse("PLANT-gradP: the plant did not change the file; the substitution "
               "did not match, so the control would certify a reader it never fed.")
    dst.write_text(planted)
    got = read_gradP_disk(dst)
    if abs(got - PLANT_GRADP) > 1e-15 * max(1.0, abs(PLANT_GRADP)):
        refuse("PLANT-gradP: planted %.9e on disk, the reader returned %.9e. A zero "
               "from a reader not shown able to see a non-zero is not evidence."
               % (PLANT_GRADP, got))
    real = read_gradP_disk(src)
    if abs(real - PLANT_GRADP) <= 1e-15:
        refuse("PLANT-gradP: the reader returns the planted value on the UNPLANTED "
               "file; it is a constant, not a reader.")
    return got, real


def planted_control_Kint(case, end, ncells, tmp):
    d = Path(case) / str(end)
    v = read_scalar_internal(d / "V", ncells)
    tot = sum(v)
    work = Path(tmp) / "kint"
    (work / str(end)).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(d / "V", work / str(end) / "V")

    # (a) k planted uniformly on disk: the integral must be PLANT_KUNIFORM * sum(V)
    ktxt = (d / "k").read_text()
    body, endpos = _entry_after(ktxt, "internalField")
    if body is None:
        refuse("PLANT-Kint: no internalField entry in the real k field")
    kind, vals = read_field_list(d / "k", "internalField", 1)
    if kind == "uniform":
        newbody = " uniform %.17g" % PLANT_KUNIFORM
    else:
        newbody = (" nonuniform List<scalar>\n%d\n(\n" % len(vals)
                   + "\n".join("%.17g" % PLANT_KUNIFORM for _ in vals) + "\n)\n")
    planted = ktxt[:endpos - len(body)] + newbody + ktxt[endpos:]
    (work / str(end) / "k").write_text(planted)
    got = f_Kint(work, end, ncells)
    want = PLANT_KUNIFORM * tot
    if abs(got - want) > 1e-9 * abs(want):
        refuse("PLANT-Kint(a): planted k = %.17g on disk over sum(V) = %.12g, so the "
               "integral must be %.12g; the reader returned %.12g."
               % (PLANT_KUNIFORM, tot, want, got))

    # (b) a single cell perturbed by a known amount at a known index
    if kind == "uniform":
        base = [vals[0]] * ncells
    else:
        base = list(vals)
    idx = ncells // 3
    delta = PLANT_K - base[idx]
    base[idx] = PLANT_K
    newbody = (" nonuniform List<scalar>\n%d\n(\n" % len(base)
               + "\n".join("%.17g" % x for x in base) + "\n)\n")
    (work / str(end) / "k").write_text(ktxt[:endpos - len(body)] + newbody + ktxt[endpos:])
    got_b = f_Kint(work, end, ncells)
    real = f_Kint(case, end, ncells)
    want_b = real + delta * v[idx]
    if abs(got_b - want_b) > 1e-7 * max(1.0, abs(want_b)):
        refuse("PLANT-Kint(b): perturbing cell %d on disk by %.9g must move the "
               "integral by %.9g to %.12g; the reader returned %.12g -- it is not "
               "reading per-cell values at the right index."
               % (idx, delta, want_b, want_b, got_b))
    return want, got_b, real


SYNTH_HDR = """FoamFile
{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      %s;
}
dimensions      [0 0 0 0 0 0 0];
internalField   uniform (0 0 0);
boundaryField
{
    bottomWall
    {
        type            calculated;
        value           nonuniform List<vector>
%d
(
%s
)
;
    }
}
"""


def planted_control_xr(tmp):
    """Synthesise a wall-shear profile on disk with a KNOWN crossing at
    PLANT_XR, and require the finder to recover it.  Then remove the crossing
    and require the finder to REFUSE rather than return a number."""
    work = Path(tmp) / "xr"
    work.mkdir(parents=True, exist_ok=True)
    n = 64
    xs = [9.0 * (i + 0.5) / n for i in range(n)]
    tau = [(x - PLANT_XR) for x in xs]          # crosses -> + exactly at PLANT_XR
    tp = work / "wallShearStress"
    cp = work / "C"
    tp.write_text(SYNTH_HDR % ("wallShearStress", n,
                               "\n".join("(%.17g 0 0)" % t for t in tau)))
    cp.write_text(SYNTH_HDR % ("C", n, "\n".join("(%.17g 0.5 0)" % x for x in xs)))
    xr, ncross = reattachment(tp, cp)
    if abs(xr - PLANT_XR) > 1e-9:
        refuse("PLANT-xr: a crossing planted on disk at x = %.6f was read back as "
               "%.6f. The crossing finder cannot see a crossing it is shown."
               % (PLANT_XR, xr))
    if ncross != 1:
        refuse("PLANT-xr: the planted profile has exactly one crossing, the finder "
               "counted %d" % ncross)
    # inverse: no crossing at all -> must refuse, not return
    tp.write_text(SYNTH_HDR % ("wallShearStress", n,
                               "\n".join("(1.0 0 0)" for _ in tau)))
    try:
        reattachment(tp, cp)
    except Refusal:
        return xr, ncross
    refuse("PLANT-xr: a profile with NO crossing did not make the finder refuse; a "
           "value it returns there would be manufactured.")


# --------------------------------------------------------------------------
# PLANTED CONTROL ON THE FATAL CHANNEL -- rule 3, new in G1b, BOTH DIRECTIONS.
# This is the control G1 lacked and the reason this successor exists.  Every
# fixture is a REAL FILE written to a TemporaryDirectory and read back through
# the SAME parse_log() the real run logs go through.
# --------------------------------------------------------------------------
SYNTH_LOG_HEAD = r"""/*---------------------------------------------------------------------------*\
| =========                 |                                                 |
|  \\    /   O peration     | Version:  2606                                  |
\*---------------------------------------------------------------------------*/
Build  : _synthetic-fixture
Exec   : simpleFoam
nProcs : 1
""" + TRAPFPE_BANNER + """
memory pool : not available
fileModificationChecking : Monitoring run-time modified files
Create time

"""

SYNTH_LOG_STEP = """Time = 1

smoothSolver:  Solving for Ux, Initial residual = 1e-06, Final residual = 1e-09, No Iterations 3
GAMG:  Solving for p, Initial residual = 1e-05, Final residual = 1e-08, No Iterations 5
Pressure gradient source: uncorrected Ubar = 1, pressure gradient = 0.001
ExecutionTime = 1.0 s  ClockTime = 1 s

"""

# Each fixture body carries EXACTLY ONE of the repaired signatures, so a single
# alternative cannot stand in for the others.  The last is a realistic combined
# sigFpe stack trace of the shape OpenFOAM actually prints.
SYNTH_FATAL_BODIES = (
    ("FOAM FATAL ERROR", "FOAM FATAL ERROR",
     "--> FOAM FATAL ERROR: (openfoam-2606)\n"
     "Cannot find patchField entry for movingWall\n\n"
     "    From function readFields()\n\nFOAM exiting\n"),
    ("FOAM FATAL IO ERROR", "FOAM FATAL IO ERROR",
     "--> FOAM FATAL IO ERROR: (openfoam-2606)\n"
     "keyword nuTilda is undefined in dictionary\n\nFOAM exiting\n"),
    ("sigFpe handler fired", "sigFpe::sigHandler",
     "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"),
    ("sigSegv handler fired", "sigSegv::sigHandler",
     "#1  Foam::sigSegv::sigHandler(int) at ??:?\n"),
    ("stack trace printed", "Foam::error::printStack",
     "#0  Foam::error::printStack(Foam::Ostream&) at ??:?\n"),
    ("shell FPE death message", "Floating point exception",
     "Floating point exception (core dumped)\n"),
    ("shell SEGV death message", "Segmentation fault",
     "Segmentation fault (core dumped)\n"),
    ("realistic sigFpe stack trace", "sigFpe::sigHandler",
     "#0  Foam::error::printStack(Foam::Ostream&) at ??:?\n"
     "#1  Foam::sigFpe::sigHandler(int) at ??:?\n"
     "#2  ? in /lib/x86_64-linux-gnu/libc.so.6\n"
     "#3  Foam::GAMGSolver::scale(...) at ??:?\n"
     "Floating point exception (core dumped)\n"),
)


def planted_control_fatal(tmp):
    """Rule 3 on the fatal channel.  Returns (positive_labels, negative_label).

    Direction (+): eight logs, each carrying ONE genuine failure signature (and
    the trapFpe banner too, exactly as a real log would) -- the reader MUST
    report fatal=True, and for the RIGHT signature.
    Direction (-): one clean log carrying the trapFpe banner VERBATIM and an
    `End` line -- the reader MUST report fatal=False.  Without this direction a
    fatal detector is indistinguishable from a constant, which is the G1 defect.
    """
    work = Path(tmp) / "fatal"
    work.mkdir(parents=True, exist_ok=True)

    # transcription controls: the two recorded strings must be what the record
    # says they are, or the whole diagnosis rests on a mis-quote.
    if not RE_G1_FATAL_CLAUSE.search(TRAPFPE_BANNER):
        refuse("PLANT-fatal: the transcribed G1 clause does NOT match the "
               "transcribed trapFpe banner. One of the two strings is not what "
               "this record claims, and the diagnosis would rest on a mis-quote.")
    if RE_FATAL.search(TRAPFPE_BANNER + "\n"):
        refuse("PLANT-fatal: the REPAIRED clause matches the trapFpe banner line "
               "itself; it is the G1 defect wearing a new pattern.")

    seen = []
    for i, (label, token, body) in enumerate(SYNTH_FATAL_BODIES):
        p = work / ("log.pos%02d" % i)
        p.write_text(SYNTH_LOG_HEAD + SYNTH_LOG_STEP + body)
        got = parse_log(p)
        if not got["fatal"]:
            refuse("PLANT-fatal(+): a log carrying a REAL %s was written to %s and "
                   "read back through parse_log as fatal=False. A fatal detector "
                   "that cannot see a real failure is not a detector."
                   % (label, p))
        if token not in got["fatal_hits"]:
            refuse("PLANT-fatal(+): the %s fixture read back fatal=True but the hit "
                   "list %r does not contain %r; it fired for the wrong reason, "
                   "which is not evidence." % (label, got["fatal_hits"], token))
        seen.append("%s (%r)" % (label, token))

    q = work / "log.neg"
    q.write_text(SYNTH_LOG_HEAD + SYNTH_LOG_STEP + "End\n")
    txt = q.read_text()
    if TRAPFPE_BANNER not in txt:
        refuse("PLANT-fatal(-): the clean fixture at %s does not carry the trapFpe "
               "banner verbatim, so a fatal=False there would prove nothing about "
               "the banner." % q)
    if not RE_G1_FATAL_CLAUSE.search(txt):
        refuse("PLANT-fatal(-): the G1 clause does NOT fire on the clean fixture at "
               "%s, so the fixture does not reproduce the defect and this control "
               "certifies nothing." % q)
    got = parse_log(q)
    if got["fatal"]:
        refuse("PLANT-fatal(-): a CLEAN log whose only match is the trapFpe banner "
               "%r was read back as fatal=True. A fatal detector never shown able "
               "to return NOT-fatal is a constant, not a reader -- which is exactly "
               "the G1 defect this successor was built to repair."
               % TRAPFPE_BANNER)
    if got["fatal_hits"]:
        refuse("PLANT-fatal(-): the clean fixture reported fatal=False but a "
               "non-empty hit list %r; the two channels disagree."
               % (got["fatal_hits"],))
    if not got["end"]:
        refuse("PLANT-fatal(-): the clean fixture carries `End` on disk and the "
               "reader did not see it; the fixture is not what it claims.")
    if got["banner_hits"] < 1 or got["legacy_hits"] < 1:
        refuse("PLANT-fatal(-): the banner counter saw legacy=%d banner=%d in a "
               "fixture that carries the banner line."
               % (got["legacy_hits"], got["banner_hits"]))
    return seen, "clean log + trapFpe banner verbatim + End"


# --------------------------------------------------------------------------
# READ-ONLY WITNESS.  A stat digest of the run root, taken before and after the
# grading pass.  This comparator is required to be strictly read-only; if the
# digest moves, it wrote to the evidence and its verdict is void.  Stat only --
# no file is opened by the witness.
# --------------------------------------------------------------------------
def readonly_witness(root):
    root = Path(root)
    h = hashlib.sha256()
    n = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            try:
                st = p.lstat()
            except OSError as exc:
                refuse("READ-ONLY WITNESS: cannot stat %s (%s)" % (p, exc))
            h.update(("%s|%d|%d\n" % (p.relative_to(root), st.st_size,
                                      st.st_mtime_ns)).encode())
            n += 1
    return h.hexdigest(), n


def self_sha256():
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# strict completion, per level.  PHYSICS clauses refuse; INFRASTRUCTURE clauses
# are named and recorded (L-342).
# --------------------------------------------------------------------------
def completion(case, end, ncells):
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
    if not log["end"]:
        phys.append("P2 End: log.run holds no `End` line")
    if log["fatal"]:
        phys.append("P3 fatal: log.run holds real failure evidence %r (repaired "
                    "clause -- see the FATAL DETECTION block; the trapFpe "
                    "'trapping enabled' banner is NOT failure evidence)"
                    % (sorted(set(log["fatal_hits"]))[:6],))

    times = sorted((c.name for c in case.iterdir()
                    if c.is_dir() and TIME_DIR.match(c.name)), key=float)
    if not times:
        phys.append("P4 time dirs: none")
    elif float(times[-1]) != float(end):
        phys.append("P4 last time: %s, registered endTime %s" % (times[-1], end))

    d = case / str(end)
    need = list(REQ_FIELDS) + ["uniform/momentumSourceProperties"]
    missing = [f for f in need if not (d / f).is_file()]
    if missing:
        phys.append("P5 fields at endTime: missing %r" % missing)

    marker = case / AGE_MARKER
    if not marker.is_file():
        phys.append("P6 age guard: marker %s absent" % marker)
    elif not missing:
        t0 = marker.stat().st_mtime
        stale = [f for f in need if (d / f).stat().st_mtime <= t0]
        if stale:
            phys.append("P6 age guard: %r at endTime are NOT newer than %s; they "
                        "cannot be the answer this run produced" % (stale, AGE_MARKER))

    if log["exec_count"] != int(end):
        phys.append("P7 ExecutionTime lines: %d, registered endTime %d. (This is the "
                    "L-342 clause: if the cause is a solver that prints extra lines, "
                    "it is triaged by the supervisor, never reclassified here.)"
                    % (log["exec_count"], int(end)))

    cm = case / "log.checkMesh"
    if not cm.is_file() or "Mesh OK" not in cm.read_text(errors="replace"):
        infra.append("I1 checkMesh: log absent or not `Mesh OK`")
    mt = case / "mem_time.txt"
    if not mt.is_file() or "Maximum resident set size" not in mt.read_text(errors="replace"):
        infra.append("I2 MaxRSS: no /usr/bin/time -v reading recorded")
    if not (case / "wall_s.txt").is_file():
        infra.append("I3 wall_s: not recorded; the cost calibration has no actual")
    if log["banner_hits"]:
        infra.append("I5 legacy-fatal-clause evidence: the G1 clause "
                     "`FOAM FATAL|Floating point exception|signal` matches %d "
                     "line(s) of this log.run, of which %d are the trapFpe "
                     "'trapping enabled' banner -- a safety notice emitted on a "
                     "healthy start, not a failure. Recorded as INFRASTRUCTURE "
                     "(L-342): it carries the evidence of the defect this "
                     "successor repairs and can never void the physics."
                     % (log["legacy_hits"], log["banner_hits"]))
    for f in ("V", "C", "wallShearStress", "yPlus"):
        if not (d / f).is_file():
            infra.append("I4 postProcessing: %s absent at endTime (the secondaries "
                         "that need it become NOT A RESULT; the primary does not "
                         "need it)" % f)
    return phys, infra, log


def iterative(log, end):
    fails = []
    for name in RES_REQUIRED:
        if name not in log["final_res"]:
            fails.append("IC1 residual: no `Solving for %s` in the final Time block" % name)
        elif log["final_res"][name] > RES_MAX[name]:
            fails.append("IC1 residual: %s final initial-residual %.3e > registered %.0e"
                         % (name, log["final_res"][name], RES_MAX[name]))
    g = log["gradP_hist"]
    if len(g) < 10:
        fails.append("IC2 plateau: only %d gradP prints in the log" % len(g))
    else:
        ntail = max(2, int(len(g) * PLATEAU_TAIL_FRAC))
        tail = g[-ntail:]
        ge = g[-1]
        if ge == 0.0:
            fails.append("IC2 plateau: final gradP is exactly zero")
        else:
            dev = max(abs(x - ge) for x in tail) / abs(ge)
            if dev > PLATEAU_RTOL:
                fails.append("IC2 plateau: over the final %d of %d iterations gradP "
                             "moves %.3e relative, registered ceiling %.0e"
                             % (ntail, len(g), dev, PLATEAU_RTOL))
    return fails


# --------------------------------------------------------------------------
# Roache
# --------------------------------------------------------------------------
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


def roache(f_coarse, f_med, f_fine, floor_mode, floor):
    label, R, e21, e32 = classify(f_coarse, f_med, f_fine, floor_mode, floor)
    out = {"label": label, "R": R, "eps21": e21, "eps32": e32,
           "p": None, "f_ext": None, "gci_pct": None}
    if label != "CONVERGING":
        # Rule 5: no GCI is computed, let alone printed, off the monotone branch.
        return out
    if R21 != R32:
        refuse("ROACHE: this comparator is frozen at constant r; r21=%g r32=%g" % (R21, R32))
    p = math.log(abs(e32 / e21)) / math.log(R21)
    denom = R21 ** p - 1.0
    if denom <= 0.0:
        refuse("ROACHE: r^p - 1 = %g is not positive; the extrapolation is undefined" % denom)
    f_ext = f_fine + e21 / denom
    if f_fine == 0.0:
        refuse("ROACHE: fine-grid value is exactly zero; a relative GCI is undefined")
    out.update(p=p, f_ext=f_ext,
               gci_pct=100.0 * FS * abs(e21 / f_fine) / denom)
    return out


def verdict_for(res, p_lo, p_hi, gci_max):
    if res["label"] != "CONVERGING":
        return "NOT A RESULT"
    if not (p_lo <= res["p"] <= p_hi):
        return "GATE FAIL"
    if res["gci_pct"] > gci_max:
        return "GATE FAIL"
    return "PASS"


# --------------------------------------------------------------------------
# grading
# --------------------------------------------------------------------------
def grade(run_root=RUN_ROOT):
    no_assert_control()
    run_root = Path(run_root)
    if not run_root.is_dir():
        refuse("RUN-ROOT: %s does not exist; there is nothing to grade" % run_root)

    print("=" * 78)
    print("G1b GRID TRIPLE REGRADE -- comparator  (FROZEN)")
    print("  The grading path is fixed at the G1b pre-registration commit. Verify")
    print("  this file IS the file that ran by hashing it against that blob:")
    print("  comparator sha256 : %s" % self_sha256())
    print("  G1 is graded NOT A RESULT; that verdict is permanent and is not")
    print("  revised here. grade_g1.py is frozen and is not edited.")
    print("  run root : %s" % run_root)
    print("             READ-ONLY -- nothing under it is written, touched or")
    print("             chmodded; every plant goes to a TemporaryDirectory.")
    print("  D = %d (one cell in z between `empty` patches: the z direction carries "
          "no\n      discretisation, so the representative cell size is "
          "h = (A/N)^(1/2))" % D_SPATIAL)
    print("  r21 = %.4f   r32 = %.4f   Fs = %.2f" % (R21, R32, FS))
    print("=" * 78)

    # ---- refinement-family control ---------------------------------------
    print("\n[FAMILY CONTROL]")
    dicts, counts = {}, {}
    for name, ncells, end in LEVELS:
        bmd = run_root / name / "system/blockMeshDict"
        own = run_root / name / "constant/polyMesh/owner"
        if not bmd.is_file():
            refuse("FAMILY: %s absent" % bmd)
        if not own.is_file():
            refuse("FAMILY: %s absent" % own)
        dicts[name] = bmd.read_text()
        m = re.search(r"nCells:\s*(\d+)", own.read_text(errors="replace")[:4000])
        if m is None:
            refuse("FAMILY: %s carries no nCells note" % own)
        counts[name] = int(m.group(1))
        if counts[name] != ncells:
            refuse("FAMILY: %s meshed to %d cells, registered %d"
                   % (name, counts[name], ncells))

    def nonhex(t):
        return "\n".join(ln for ln in t.split("\n")
                         if not ln.startswith("        hex ")).encode()

    def verts(t):
        m = re.search(r"(?m)^vertices\n\(\n.*?^\);\n", t, re.S)
        if m is None:
            refuse("FAMILY: a dictionary has no vertices block")
        return m.group(0).encode()

    ref = LEVELS[0][0]
    for name, _n, _e in LEVELS[1:]:
        if verts(dicts[name]) != verts(dicts[ref]):
            refuse("FAMILY: the vertices block of %s differs from %s BYTE-WISE. "
                   "This is the alpha_10_9000_{2024,3036,4048} shape: three dirs "
                   "that look like a refinement family and are three GEOMETRIES "
                   "(measured: nCells 15600 for all three, three different "
                   "vertices sha256)." % (name, ref))
        if nonhex(dicts[name]) != nonhex(dicts[ref]):
            refuse("FAMILY: %s differs from %s outside the two hex block lines" % (name, ref))
    cs = [counts[n] for n, _x, _y in LEVELS]
    if len(set(cs)) != 3:
        refuse("FAMILY: the three cell counts %r are not distinct" % (cs,))
    if cs[1] != 4 * cs[0] or cs[2] != 4 * cs[1]:
        refuse("FAMILY: cell counts %r are not in the registered 1:4:16 ratio" % (cs,))
    print("  vertices block byte-identical across L1/L2/L3          VERIFIED")
    print("  all bytes outside the two hex lines byte-identical      VERIFIED")
    print("  nCells %d / %d / %d -- distinct, exact 1:4:16           VERIFIED"
          % tuple(cs))

    # ---- planted control on the FATAL CHANNEL (rule 3) --------------------
    # This runs BEFORE the completion clauses that consume it. A control placed
    # after them would never execute on a run the fatal clause blocks -- which
    # is exactly the run G1 produced.
    print("\n[PLANTED CONTROL -- FATAL CHANNEL, rule 3, BOTH DIRECTIONS]")
    with tempfile.TemporaryDirectory() as tmp:
        fatal_pos, fatal_neg = planted_control_fatal(tmp)
        for lab in fatal_pos:
            print("  planted ON DISK  %-46s -> fatal=True" % lab)
        print("  planted ON DISK  %-46s -> fatal=False" % fatal_neg)
    print("    The negative direction is the point: that clean fixture carries the")
    print("    trapFpe banner VERBATIM and the G1 clause DOES fire on it, so a")
    print("    reader that returns fatal=False there is a reader and not a constant.")

    # ---- completion + iterative convergence ------------------------------
    print("\n[COMPLETION AND ITERATIVE CONVERGENCE]")
    infra_all, blocked = [], []
    logs = {}
    for name, ncells, end in LEVELS:
        case = run_root / name
        phys, infra, log = completion(case, end, ncells)
        logs[name] = log
        it = iterative(log, end) if not phys else []
        infra_all += ["%s %s" % (name, x) for x in infra]
        if phys or it:
            blocked.append((name, phys + it))
            print("  %s  REFUSED" % name)
            for x in phys + it:
                print("      %s" % x)
        else:
            print("  %s  complete: rc=0, End, last time == %d, fields present, age "
                  "guard held,\n        ExecutionTime lines == %d, residuals below "
                  "registry, gradP plateaued" % (name, end, end))
    for x in infra_all:
        print("  INFRASTRUCTURE DEFECT: %s" % x)

    if blocked:
        print("\n[VERDICT]")
        print("  RUNG VERDICT: NOT A RESULT")
        print("  Reason: standing rule 5 step 1 -- a level that is not complete or "
              "not\n  iteratively converged makes the triple NOT A RESULT whatever "
              "any number says.")
        return 2

    # ---- planted-disk controls -------------------------------------------
    print("\n[PLANTED CONTROLS -- rule 3, each round-tripping a real file]")
    fine, fine_n, fine_end = LEVELS[-1]
    with tempfile.TemporaryDirectory() as tmp:
        got, real = planted_control_gradP(
            run_root / fine / str(fine_end) / "uniform/momentumSourceProperties", tmp)
        print("  gradP reader saw a %.6e planted ON DISK and returned %.6e, and does "
              "NOT\n    return it on the unplanted file (%.9g)" % (PLANT_GRADP, got, real))
        try:
            want, got_b, kreal = planted_control_Kint(run_root / fine, fine_end, fine_n, tmp)
            print("  volume integrator: k planted uniformly ON DISK gives %.9g, the "
                  "closed form;\n    a single-cell plant moves it to %.9g; real "
                  "integral %.9g" % (want, got_b, kreal))
            kint_ok = True
        except Refusal as exc:
            print("  volume integrator control REFUSED: %s" % exc)
            kint_ok = False
        xr_planted, _nc = planted_control_xr(tmp)
        print("  crossing finder recovered a crossing planted ON DISK at x = %.6f, "
              "and\n    REFUSES on a profile with none" % xr_planted)

    # ---- functionals ------------------------------------------------------
    print("\n[FUNCTIONALS]")
    vals = {"gradP": {}, "Kint": {}, "xr": {}}
    ncross = {}
    notes = {}
    for name, ncells, end in LEVELS:
        case = run_root / name
        vals["gradP"][name] = f_gradP(case, end)
        dg = abs(vals["gradP"][name] - logs[name]["gradP_hist"][-1])
        if dg > DISK_VS_LOG_RTOL * abs(vals["gradP"][name]):
            refuse("gradP: the disk value %.17g and the last log value %.17g at %s "
                   "disagree by %.3e; two independent reads of one quantity must agree"
                   % (vals["gradP"][name], logs[name]["gradP_hist"][-1], name, dg))
        try:
            vals["Kint"][name] = f_Kint(case, end, ncells) if kint_ok else None
        except Refusal as exc:
            vals["Kint"][name] = None
            notes.setdefault("Kint", []).append("%s: %s" % (name, exc))
        try:
            d = case / str(end)
            x, n = reattachment(d / "wallShearStress", d / "C")
            vals["xr"][name], ncross[name] = x, n
        except Refusal as exc:
            vals["xr"][name], ncross[name] = None, None
            notes.setdefault("xr", []).append("%s: %s" % (name, exc))
    if len(set(v for v in ncross.values() if v is not None)) > 1:
        notes.setdefault("xr", []).append(
            "the tau_wx crossing COUNT differs across levels %r; the three values "
            "are not the same quantity" % (ncross,))
        for n, _a, _b in LEVELS:
            vals["xr"][n] = None

    # ---- Roache ------------------------------------------------------------
    print("\n[ROACHE TRIPLES]")
    rung = "NOT A RESULT"
    for key, label, unit, p_lo, p_hi, gci_max, fmode, floor in FUNCTIONALS:
        print("\n  %s  [%s]  unit %s" % (key, label, unit))
        for n in notes.get(key, []):
            print("      note: %s" % n)
        triple = [vals[key][n] for n, _a, _b in LEVELS]
        if any(t is None for t in triple):
            print("      L1/L2/L3 = %r" % (triple,))
            print("      VERDICT: NOT A RESULT (a level has no value)")
            if key == "gradP":
                rung = "NOT A RESULT"
            continue
        print("      L1 (coarse, %6d cells) = %.12g" % (LEVELS[0][1], triple[0]))
        print("      L2 (medium, %6d cells) = %.12g" % (LEVELS[1][1], triple[1]))
        print("      L3 (fine,   %6d cells) = %.12g" % (LEVELS[2][1], triple[2]))
        res = roache(triple[0], triple[1], triple[2], fmode, floor)
        print("      eps21 = %.6g   eps32 = %.6g   R = %s"
              % (res["eps21"], res["eps32"],
                 "n/a" if res["R"] is None else "%.6g" % res["R"]))
        print("      TRIPLE: %s" % res["label"])
        v = verdict_for(res, p_lo, p_hi, gci_max)
        if res["label"] == "CONVERGING":
            # printed from INSIDE the branch that established monotonicity
            print("      observed order p = %.4f (registered band [%.2f, %.2f])"
                  % (res["p"], p_lo, p_hi))
            print("      Richardson extrapolate = %.12g" % res["f_ext"])
            print("      GCI_fine (Fs=%.2f)      = %.4f %%  (registered ceiling %.2f %%)"
                  % (FS, res["gci_pct"], gci_max))
        else:
            print("      no order and no GCI are quoted: the three values are not "
                  "monotone.")
        print("      VERDICT: %s" % v)
        if v not in VERDICTS:
            refuse("VERDICT: %r is not in the fixed vocabulary" % v)
        if key == "gradP":
            rung = v

    print("\n[VERDICT]")
    print("  RUNG VERDICT (from the PRIMARY functional gradP): %s" % rung)
    print("  The secondaries never change it.")
    print("  This rung grades NUMERICAL CONVERGENCE ONLY. It says nothing whatever "
          "about\n  agreement with LES or DNS truth: no reference field is read, and "
          "none exists\n  on the L1 or L3 meshes.")
    for x in infra_all:
        print("  INFRASTRUCTURE DEFECT carried into the record: %s" % x)
    return 0 if rung == "PASS" else 1


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------
def _must_refuse(label, fn):
    try:
        fn()
    except Refusal as exc:
        print("  REFUSAL FIRED  %-32s %s" % (label, str(exc).split("\n")[0][:90]))
        return True
    print("  REFUSAL DID NOT FIRE  %s" % label)
    return False


def selftest():
    ok = True
    print("SELFTEST: assert-counter control")
    planted, own = no_assert_control()
    if planted != 1 or own != 0:
        print("  CONTROL FAILED"); ok = False
    else:
        print("  counter saw the planted assert (1) and none in this module (0)")

    print("SELFTEST: Roache classification, known answers")
    cases = (
        # f_exact + C h^p with h = 4, 2, 1 -> CONVERGING, p recovered exactly
        ("CONVERGING", (2.6, 1.4, 1.1), 2.0),
        ("DIVERGENT", (1.0, 1.4, 2.6), None),
        ("OSCILLATORY", (1.0, 2.0, 1.5), None),
        ("EXACT", (1.0, 1.0, 1.0), None),
        ("STAGNANT", (1.0, 1.4, 1.4), None),
    )
    for want, (fc, fm, ff), want_p in cases:
        r = roache(fc, fm, ff, "rel", 1e-4)
        good = r["label"] == want and (want_p is None or abs(r["p"] - want_p) < 1e-12)
        print("  %-12s -> %-12s %s" % (want, r["label"],
              "" if want_p is None else "p=%.10f" % r["p"]))
        if not good:
            print("    CLASSIFICATION FAILED"); ok = False
        if r["label"] != "CONVERGING" and r["gci_pct"] is not None:
            print("    A GCI WAS COMPUTED OFF THE MONOTONE BRANCH"); ok = False
    r = roache(2.6, 1.4, 1.1, "rel", 1e-4)
    if abs(r["f_ext"] - 1.0) > 1e-12 or abs(r["gci_pct"] - 11.3636363636) > 1e-6:
        print("  RICHARDSON/GCI CLOSED FORM FAILED: f_ext=%r gci=%r"
              % (r["f_ext"], r["gci_pct"])); ok = False
    else:
        print("  Richardson extrapolate recovers the exact value 1.0 and "
              "GCI = %.6f %%" % r["gci_pct"])

    print("SELFTEST: planted-disk controls on synthetic files")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        # gradP round trip on a real-shaped file
        f = t / "momentumSourceProperties"
        f.write_text("FoamFile{}\n\ngradient        0.00843952091409712;\n")
        got, real = planted_control_gradP(f, t / "sub") if (t / "sub").mkdir() or True else (0, 0)
        if abs(got - PLANT_GRADP) > 1e-15 or abs(real - 0.00843952091409712) > 1e-15:
            print("  PLANT-gradP FAILED"); ok = False
        else:
            print("  PLANT-gradP: planted %.6e read back; unplanted file reads %.9g"
                  % (got, real))
        xr, n = planted_control_xr(t)
        if abs(xr - PLANT_XR) > 1e-9 or n != 1:
            print("  PLANT-xr FAILED"); ok = False
        else:
            print("  PLANT-xr: crossing planted at %.4f recovered as %.10f" % (PLANT_XR, xr))
        # a reader that cannot see the plant MUST make the control refuse
        ok &= _must_refuse("PLANT-gradP blind reader", lambda: (
            (t / "blind").mkdir(exist_ok=True),
            _blind_gradP_control(f, t / "blind"))[1])
        # a crossing finder fed a profile with no crossing must refuse
        ok &= _must_refuse("xr no crossing", lambda: _no_crossing(t))

    print("SELFTEST: planted control on the FATAL channel, both directions")
    with tempfile.TemporaryDirectory() as tmp:
        pos, neg = planted_control_fatal(tmp)
        print("  %d isolated real-failure signatures, each written to disk and each"
              % len(pos))
        print("    read back fatal=True FOR ITS OWN SIGNATURE")
        print("  %s -> read back fatal=False" % neg)
        ok &= _must_refuse("fatal reader stuck TRUE",
                           lambda: _blind_fatal_control(tmp, r"(?s).*"))
        ok &= _must_refuse("fatal reader stuck FALSE",
                           lambda: _blind_fatal_control(tmp, r"(?!x)x"))

    print("SELFTEST: read-only witness")
    with tempfile.TemporaryDirectory() as tmp:
        tr = Path(tmp) / "tree" / "a"
        tr.mkdir(parents=True)
        (tr / "f.txt").write_text("one")
        base = Path(tmp) / "tree"
        w1 = readonly_witness(base)
        w2 = readonly_witness(base)
        (tr / "f.txt").write_text("two-much-longer")
        w3 = readonly_witness(base)
        (tr / "g.txt").write_text("x")
        w4 = readonly_witness(base)
        if w1 != w2:
            print("  WITNESS UNSTABLE ON AN UNCHANGED TREE"); ok = False
        elif w3 == w1 or w4 == w3:
            print("  WITNESS BLIND TO A CHANGE IT WAS SHOWN"); ok = False
        else:
            print("  witness: identical twice over an unchanged tree (%d file), and"
                  % w1[1])
            print("    changed by an edited file AND by an added file")

    print("SELFTEST: readers")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        p = t / "k"
        p.write_text("FoamFile{}\ninternalField   nonuniform List<scalar>\n3\n(\n1\n2\n3\n)\n;\n"
                     "boundaryField{}\n")
        v = read_scalar_internal(p, 3)
        if v != [1.0, 2.0, 3.0]:
            print("  READER nonuniform FAILED: %r" % v); ok = False
        else:
            print("  reader: nonuniform scalar list read as %r" % v)
        p.write_text("FoamFile{}\ninternalField   uniform 7;\nboundaryField{}\n")
        v = read_scalar_internal(p, 4)
        if v != [7.0] * 4:
            print("  READER uniform FAILED: %r" % v); ok = False
        else:
            print("  reader: uniform scalar expanded to %r" % v)
        p.write_text("FoamFile{}\ninternalField   nonuniform List<scalar>\n3\n"
                     "(\n1\n2\n3\n)\n;\nboundaryField{}\n")
        ok &= _must_refuse("reader wrong length",
                           lambda: read_scalar_internal(t / "k", 9))
        ok &= _must_refuse("reader missing file",
                           lambda: read_scalar_internal(t / "nope", 3))
        ok &= _must_refuse("gradP missing entry",
                           lambda: read_gradP_disk(t / "k"))

    print("SELFTEST: verdict vocabulary")
    for lab, exp in (("CONVERGING", None), ("DIVERGENT", "NOT A RESULT"),
                     ("OSCILLATORY", "NOT A RESULT"), ("STAGNANT", "NOT A RESULT"),
                     ("EXACT", "NOT A RESULT")):
        v = verdict_for({"label": lab, "p": 2.0, "gci_pct": 1.0}, 1.0, 3.0, 5.0)
        if exp and v != exp:
            print("  VERDICT MAP FAILED for %s -> %s" % (lab, v)); ok = False
    if verdict_for({"label": "CONVERGING", "p": 0.2, "gci_pct": 1.0}, 1.0, 3.0, 5.0) != "GATE FAIL":
        print("  p out of band did not give GATE FAIL"); ok = False
    if verdict_for({"label": "CONVERGING", "p": 2.0, "gci_pct": 99.0}, 1.0, 3.0, 5.0) != "GATE FAIL":
        print("  GCI over ceiling did not give GATE FAIL"); ok = False
    if verdict_for({"label": "CONVERGING", "p": 2.0, "gci_pct": 1.0}, 1.0, 3.0, 5.0) != "PASS":
        print("  a good triple did not give PASS"); ok = False
    print("  a non-CONVERGING triple maps to NOT A RESULT for every label; p out of "
          "band\n  and GCI over ceiling each map to GATE FAIL; only a CONVERGING "
          "triple inside\n  both registered bands maps to PASS")

    if ok:
        print("SELFTEST PASS: every registered refusal fired, every planted control "
              "was\nseen, and the Roache closed forms were recovered exactly.")
        return 0
    print("SELFTEST FAIL")
    return 2


def _blind_gradP_control(real_path, tmp):
    """A deliberately blind reader: the control must catch it."""
    global read_gradP_disk
    keep = read_gradP_disk
    try:
        read_gradP_disk = lambda _p: 0.0        # noqa: E731  -- the blind reader
        return planted_control_gradP(real_path, tmp)
    finally:
        read_gradP_disk = keep


def _blind_fatal_control(tmp, pattern):
    """Swap in a deliberately blind fatal pattern.  The planted control must
    catch it in BOTH directions: a pattern stuck TRUE fails the negative
    direction, a pattern stuck FALSE fails the positive one."""
    global RE_FATAL
    keep = RE_FATAL
    try:
        RE_FATAL = re.compile(pattern, re.M)
        return planted_control_fatal(Path(tmp) / ("blind%d" % len(pattern)))
    finally:
        RE_FATAL = keep


def _no_crossing(t):
    work = t / "nox"
    work.mkdir(exist_ok=True)
    n = 16
    xs = [9.0 * (i + 0.5) / n for i in range(n)]
    (work / "wallShearStress").write_text(
        SYNTH_HDR % ("wallShearStress", n, "\n".join("(1.0 0 0)" for _ in xs)))
    (work / "C").write_text(
        SYNTH_HDR % ("C", n, "\n".join("(%.17g 0.5 0)" % x for x in xs)))
    return reattachment(work / "wallShearStress", work / "C")


def main(argv):
    try:
        if "--selftest" in argv:
            return selftest()
        root = RUN_ROOT
        for i, a in enumerate(argv):
            if a == "--run-root" and i + 1 < len(argv):
                root = Path(argv[i + 1])
        before = readonly_witness(root) if Path(root).is_dir() else None
        rc = grade(root)
        if before is not None:
            after = readonly_witness(root)
            if after != before:
                refuse("READ-ONLY WITNESS: the run root changed during grading "
                       "(%r -> %r). This comparator is required to be strictly "
                       "read-only; a verdict produced while it wrote to the "
                       "evidence is void." % (before, after))
            print("\n  READ-ONLY WITNESS: %d files under %s, stat digest %s,"
                  % (before[1], root, before[0][:16]))
            print("    IDENTICAL before and after the grading pass.")
        return rc
    except Refusal as exc:
        sys.stderr.write("REFUSED: %s\n" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
