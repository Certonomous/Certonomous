#!/usr/bin/env python3
"""T16c -- the comparator for the successor to T16's `C_ORDER` clause.

AUTHORITY.  The only authority for every gate, threshold, band, cap and label in
this file is the FROZEN pre-registration

    docs/campaigns/T-family/T16c_PREREGISTRATION.md
    sha256 0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f
    frozen by the supervisor at commit 8ff2cf36

and, through its section 5 pin and its section 6 carry-over, T16's own frozen
`T16_registered.json`.  THIS FILE DEFINES NO GATE OF ITS OWN.  Every number it
compares against is either loaded from the pinned registration, imported from
`scripts/roache_triple.py` by name, or carried over from `analyse_t16.py` at a
line number this docstring cites.  Where the frozen document is silent, the
silence is DISCLOSED in `T16c_INSTRUMENT_DIFFS.txt` and never filled quietly.

--------------------------------------------------------------------------
WHAT T16c REPAIRS.  T16 refused three complete solves under a single clause at
`analyse_t16.py:573-576` that evaluated

    "does the station row's T match the linear profile to within 1e-06?"

while PUBLISHING

    "a transposed cell ordering".

Two propositions, six orders of magnitude apart, at one tolerance.  The ordering
was fine and the field WAS the solution; the published diagnosis was FALSE.  The
frozen document splits that clause (its section 6) into

  C_TRANSPOSE  an ORDERING guard sized to its own O(1) signal, threshold 0.5,
               admitted only under a PLANTED transposed control (section 2);
  C_PROFILE    a PROFILE-agreement gate at 1e-06 -- the tolerance CARRIED OVER
               UNCHANGED -- applied at a station chosen by the frozen RULE of
               section 4, i.e. moved to where the referent is valid rather than
               loosened;

and moves `W1_T`, the witness that carried verification's entire diagnosis and
sat NINE LINES BELOW the guard that made it unreachable, ABOVE both (section 3;
D576's shape).

--------------------------------------------------------------------------
SECTION 2a OF THE VERIFICATION CHARTER -- each gate declares, at creation, what
would make it FAIL and how a wrong treatment could still PASS it.

  C_TRANSPOSE (|slope/(-dT) - 1| <= 0.5, section 1 line 4)
    FAILS ON: a row read through a transposed (y-fastest) ordering, which walks
      an isothermal column, so slope ~ 0 and the statistic goes to -1.0; also a
      uniform field, and any read that carries no hot-to-cold gradient at all.
    A WRONG TREATMENT STILL PASSES IT BY: being nearly linear and wrong in
      detail -- 0.5 is 500 000 times looser than the profile question.  THAT IS
      WHY C_PROFILE IS ALSO GATED.  The refusal text therefore names the whole
      family of causes and does NOT publish "transposed ordering" as a
      diagnosis: publishing one member of a family as if it were the finding is
      exactly the error T16c exists to repair.

  C_PROFILE (monotone AND |slope/(-dT) - 1| <= 1e-06 at the SELECTED station)
    FAILS ON: a station row whose T is not the registered hot-to-cold linear
      profile to 1e-06 -- i.e. the referent does not describe that row.
    A WRONG TREATMENT STILL PASSES IT BY: producing the right linear T with a
      wrong velocity field.  The linear T is an exact solution FOR ANY velocity
      field (`analyse_t16.py:20-30`), so C_PROFILE constrains T and NOTHING
      about v.  THAT IS WHY C_MASS, C_REV, W1_v and W1_g are also gated, and
      why G1/G1b/G3 are graded by Roache triples and not by C_PROFILE.

  THE STATION RULE (section 4)
    FAILS ON: no j in the candidate set reaching W1_T <= 1e-06 on the fine
      level (the registered unreachable branch -> NOT A RESULT), or the selected
      y/b failing that threshold on any of the three levels (the three-level
      consistency clause -> NOT A RESULT).
    A WRONG TREATMENT STILL PASSES IT BY: being STREAMWISE-UNIFORM for the wrong
      reason -- a constant T field has W1_T = 0 at the FIRST candidate row and
      is selected instantly.  It is caught downstream: C_TRANSPOSE reads -1.0
      on it and refuses, and `read_field` refuses a uniform internalField
      outright (`analyse_t16.py:269-270`).  Both are driven as selftest limbs.
    AND -- SECTION 2a'S IDENTITY TEST, WHICH THE FROZEN DOCUMENT DOES NOT MAKE:
      on the FINE level, "W1_T <= 1e-06 at the graded station" is TRUE BY
      CONSTRUCTION, because that is the criterion the station was selected by.
      It is an IDENTITY THERE, it is REPORTED AND NOT COUNTED AS EVIDENCE, and
      this file prints it as such.  On the COARSE and MEDIUM levels the same
      clause is a genuine control -- the y/b came from the fine level and those
      two can fail it -- and it is the three-level consistency clause of
      section 4 that carries all the discriminating power in this gate.

--------------------------------------------------------------------------
THE REGISTERED ORDER OF CRITERIA (section 1 line 7; "registered, not an
implementation detail"), and it is the D576 repair:

  (i)   strict completion, standing rule 4, INCLUDING THE AGE GUARD;
  (ii)  W1_v, W1_g and W1_T ARE READ AND PRINTED for ALL THREE LEVELS,
        unconditionally, BEFORE any guard can refuse;
  (iii) C_TRANSPOSE -- a refusal here is a genuine ordering-class defect;
  (iv)  station selection by the frozen rule of section 4;
  (v)   C_PROFILE and the remaining gate-(1) clauses;
  (vi)  Roache classification, then the band.

Steps (ii) and (iii) each run over ALL THREE LEVELS before the next begins.  A
per-level loop that refused at (iii) on the coarse level would destroy the
medium and fine witnesses -- which is the D576 failure with a smaller radius.

C_TRANSPOSE REFUSES (exit 2).  C_PROFILE and the station clauses are GATE (1)
clauses and return NOT A RESULT.  That division is the whole repair: T16
REFUSED ON PHYSICS.  A statement about the instrument refuses; a statement
about the solution is graded.

--------------------------------------------------------------------------
PLANTED-ZERO CONTROLS, standing rule 3.

T16's per-reader controls for G1 / G1b / G2 / G3 / W1_max are CARRIED OVER
BYTE-IDENTICALLY (frozen document section 6 carries C_PZ) and the selftest
proves that byte-identity against `analyse_t16.py` rather than promising it.

The NEW reader T16c introduces -- `w1_T_at(j)`, the station-selection metric --
gets its OWN control, and its predicate is the FAMILY'S RELATIVE FORM

    ok = (got >= PLANT * (1.0 - 1e-9)) and (got <= base + PLANT + 1e-12)

as at `T1_runs/analyse_pesweep.py:141`, `T1_runs/analyse_dts.py:594` and
`T1_runs/analyse_dts_p.py:226`, ALL THREE READ AT SOURCE.

IT IS DELIBERATELY *NOT* `analyse_t3.py:327`'s `passed = (seen >= PLANT -
1e-15)`.  That predicate is DEFECTIVE on a temperature field and the arithmetic
is not close: one ULP at 300 K is `math.ulp(300.0)` = 5.684341886080802e-14 K,
so a 1e-15 slack sits 56.84x BELOW a single ULP and the control is decided by
the sign of a several-ULP residual wiggle in a difference of two ~300 K
numbers.  The relative slack `PLANT * 1e-9` = 1.234e-12 K is 21.7 ULP -- above
the noise it must tolerate and 10^9 below the signal it must see.  The
comparator MEASURES both ratios at run time and PRINTS them, so this paragraph
is a reading and not a recollection.

The plant's SIGN is chosen to be additive against the difference already at the
planted cell.  A plant of fixed sign into a cell whose existing difference is
opposite would return `p - |d|`, which is BELOW `p * (1 - 1e-9)` for any real
|d|, and the control would red on a perfectly good reader.  The sign choice is
a property of the CONTROL, not of the gate, and it is disclosed here because a
control that quietly picks a favourable cell would be worthless.

--------------------------------------------------------------------------
S8 -- THE SELFTEST MAY NOT TOUCH THE LIVE RUN TREE.  THIS IS NOT HYPOTHETICAL.

`analyse_t18.py:509` carries `grade(HERE, ...)` with `HERE` the LIVE
`T18_runs` directory.  It fired on 2026-08-31 and produced
`T18_runs/T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.json`, which is
BYTE-IDENTICAL -- both sha256 335bbec520a20ff461398c0b7135e451b994459a7bc7f1
dfdd63700afdd7e099, MEASURED -- to the `gate_t18.json` written five minutes
later.  A selftest that touches the live tree manufactures a verdict nobody
registered, and a verdict nobody registered is indistinguishable from one
somebody did.

Five clauses, adapted from T19b's registered S8 apparatus:

  S8a  `_selftest_root_guard` REFUSES (exit 2) if a selftest arm's grading root
       is, contains, or is contained by a LIVE root.  It runs as the FIRST
       statement of `_selftest_grade`, before any read.
  S8b  every forged tree carries `FORGED_BY_T16C_SELFTEST_NOT_A_RUN` at its
       root and `_selftest_grade` REFUSES without it.  S8a alone is a path
       test and a symlink defeats it; S8b is a POSITIVE marker only the forge
       writes, and no real tree can acquire one by accident.
  S8c  a `_RootWatch` records every read under each live root for the whole
       selftest, allowing ONLY the three frozen parent instruments.  A ZERO
       FROM THAT WATCHER IS NOT EVIDENCE until it has been shown able to see a
       non-zero, so a deliberate read is PLANTED into it and checked.
  S8d  a source-level detector counts references to `HERE` and to `LIVE_ROOT`
       inside the selftest functions.  `analyse_t18.py:509` held exactly one
       such reference and that one reference is the entire defect.
  S8e  `sys.dont_write_bytecode = True` BEFORE the parent imports, so importing
       `exact_t16` and `build_t16` cannot create `T16_runs/__pycache__` --
       a WRITE into a frozen tree performed by the act of reading it.  The
       pattern and its comment are taken from `E4a2_runs/analyse_e4a2.py:47`.

--------------------------------------------------------------------------
NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is `sys.exit(2)` and
fires identically under `python3 -O`.  The verdict is written by `apply_gate()`
and by nothing else.  Exit: 0 graded, 2 REFUSAL.
"""
import argparse
import json
import math
import os
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True          # S8e: no __pycache__ in any frozen tree

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_repo(start):
    """The repository root, located STRUCTURALLY by its own CLAUDE.md.  The
    walk-up is used when this file sits in its filed location; the registered
    absolute path is the fallback that lets a SCRATCH COPY of this comparator
    (a mutation control) still find the real frozen instruments -- and still be
    stopped by S8a, which is the point."""
    d = os.path.abspath(start)
    for _ in range(8):
        if os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    return "/home/ubuntu/Certonomous"


REPO = _find_repo(HERE)

# ---- THE FROZEN PARENT INSTRUMENTS, BY ABSOLUTE PATH (frozen document sec. 5)
PARENT = os.path.join(REPO, "verification", "runs", "T-family", "T16_runs")
REG_PATH = os.path.join(PARENT, "T16_registered.json")

# REGISTERED, frozen document section 5, verbatim.  9,179 bytes.
REG_SHA256 = "aead91aaab8480f6a4321a3d9eb01536d9ceb4cbfb7a3774426cea608ae72845"

EXACT_PATH = os.path.join(PARENT, "exact_t16.py")
BUILD_PATH = os.path.join(PARENT, "build_t16.py")
T16_PATH = os.path.join(PARENT, "analyse_t16.py")

# THE LIVE RUN TREES.  S8a refuses any selftest arm pointed at one of these.
# `HERE` is included: a selftest that graded its own directory would write
# gate_t16c.json beside the frozen comparator, which is the same defect wearing
# a different path.
LIVE_ROOT = PARENT
LIVE_ROOTS = (PARENT, HERE)

FORGE_SENTINEL = "FORGED_BY_T16C_SELFTEST_NOT_A_RUN"

EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def pin(path, want, what):
    """Frozen document section 5.  A digest that does not reproduce is a
    REFUSAL, never a warning: it is the only mechanism by which "not one
    carried-over floor moved" can be a MEASUREMENT rather than a claim, because
    every floor section 1 line 4 carries over lives inside this one file."""
    if not os.path.isfile(path):
        refuse("the frozen parent instrument %s is missing at %s -- T16c grades against T16's "
               "own frozen registration and will not substitute a copy" % (what, path))
    got = sha256_of(path)
    if got != want:
        refuse("%s at %s has sha256 %s but the FROZEN T16c_PREREGISTRATION.md section 5 pins %s "
               "-- the file that would run is NOT the frozen file, so no carried-over floor can "
               "be shown to be unmoved" % (what, path, got, want))
    return got


for _p, _w in ((EXACT_PATH, "exact_t16.py"), (BUILD_PATH, "build_t16.py"), (T16_PATH, "analyse_t16.py")):
    if not os.path.isfile(_p):
        refuse("the frozen parent instrument %s is missing at %s" % (_w, _p))

sys.path.insert(0, PARENT)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import exact_t16 as EX                                                      # noqa: E402
import build_t16 as B                                                       # noqa: E402
from roache_triple import STAGNANT_FLOOR, P_MIN, FS, gci_equal, monotone    # noqa: E402
# `build_t16` is imported HERE, at module scope, and NOT inside the forge.  An
# import performed inside the selftest would run the path finder over the live
# T16_runs directory while the S8c watcher was armed, and a listdir of a live
# run tree is exactly what that watcher exists to catch -- allowing it would
# blind the watcher to the thing it was built for.

# ------------------------------------------------------------------ CONSTANTS
# CARRIED OVER BYTE-IDENTICALLY from analyse_t16.py:107-119.  Frozen document
# section 1 line 4: "Every other floor ... carried over byte-identically.  Not
# one is touched."  `_carried_over_constants_check()` proves it against the
# pinned parent rather than promising it.
LEVELS = ("c", "m", "f")
CASES = {lv: "T16_MC_%s" % lv for lv in LEVELS}
REFINEMENT = 2.0
DIM = 2
PLANT_REL = 1.234e-03          # the family's plant, as a fraction of the reader's scale
CONV_FLOOR = 1.0e-6            # the family's floor, registered; MEASURED reachable, see below
PLAT_FLOOR = 1.0e-7
W1_FLOOR_V = 2.0e-4            # development witness, WHOLE-ROW max-norm in v/U0
W1_FLOOR_G = 2.0e-5            # development witness, ON THE GRADED READER G1 itself
W1_FLOOR_T = 1.0e-6            # development witness, in T/dT
MASS_FLOOR = 1.0e-6
G_TOL = 1.0e-9

# ---- THE ONE CLAUSE THAT IS REPLACED (frozen document section 6)
# C_TRANSPOSE: REGISTERED at 0.5 in section 1 line 4, sized to the -1.0 signal
# it hunts and NOT to instrument precision.
C_TRANSPOSE_TOL = 0.5
# The signature the guard is sized against, and the tolerance the section 2
# planted control must recover it within.  REGISTERED, section 2 clause 2.
TRANSPOSE_SIGNATURE = -1.0
TRANSPOSE_SIG_TOL = 0.1
# C_PROFILE: CARRIED OVER UNCHANGED from analyse_t16.py:573.  Section 1 line 4:
# "section 18.4 clause 2 forbids relaxing it and it is not relaxed."
C_PROFILE_TOL = 1.0e-06
# The station rule's threshold IS W1_FLOOR_T (section 4 THRESHOLD: "the
# registered W1_FLOOR_T (analyse_t16.py:116).  Not a new number.").  It is bound
# to that name rather than restated, and `_station_floor_identity_check()`
# refuses if the two ever differ -- which is how "not a new number" becomes
# structural instead of a promise.
STATION_FLOOR_T = W1_FLOOR_T


def _station_floor_identity_check():
    if STATION_FLOOR_T != W1_FLOOR_T:
        refuse("the station rule's threshold %r is not W1_FLOOR_T %r -- frozen document section 4 "
               "registers T16's OWN floor and NOT a new number" % (STATION_FLOOR_T, W1_FLOOR_T))
    if C_PROFILE_TOL != 1.0e-06:
        refuse("C_PROFILE tolerance %r is not the 1e-06 carried over from analyse_t16.py:573; "
               "frozen document section 9 forbids relaxing it" % (C_PROFILE_TOL,))
    if not (C_TRANSPOSE_TOL == 0.5 and TRANSPOSE_SIGNATURE == -1.0 and TRANSPOSE_SIG_TOL == 0.1):
        refuse("C_TRANSPOSE constants %r/%r/%r are not the frozen document's 0.5 / -1.0 / 0.1"
               % (C_TRANSPOSE_TOL, TRANSPOSE_SIGNATURE, TRANSPOSE_SIG_TOL))
    return True


def load_registered(here=None):
    """CARRIED OVER from analyse_t16.py:129-148, with the section 5 PIN added on
    the production path.  `here` is the selftest's mutant-registration route and
    is NOT pinned -- pinning a deliberately mutated file would defeat the mutant
    check it exists to drive."""
    p = os.path.join(here, "T16_registered.json") if here else REG_PATH
    if not os.path.isfile(p):
        refuse("no T16_registered.json at %s" % p)
    if here is None:
        pin(p, REG_SHA256, "T16_registered.json")
    reg = json.load(open(p))
    fl = reg.get("roache_floors", {})
    if fl.get("STAGNANT_FLOOR") != STAGNANT_FLOOR or fl.get("P_MIN") != P_MIN:
        refuse("registered floors %r disagree with the imported roache_triple "
               "STAGNANT_FLOOR=%r P_MIN=%r (MESH_STANDARD 10.5: one name, one number)"
               % (fl, STAGNANT_FLOOR, P_MIN))
    ph = reg.get("physics", {})
    if abs(ph.get("G_mix", -1) - EX.G_REG) > 0.0:
        refuse("registered G_mix %r is not the referent's G_REG %r" % (ph.get("G_mix"), EX.G_REG))
    if abs(ph.get("G_reversal", -1) - EX.G_REVERSAL) > 0.0:
        refuse("registered reversal threshold %r is not the referent's DERIVED %r"
               % (ph.get("G_reversal"), EX.G_REVERSAL))
    if reg.get("grid_triple_absent"):
        refuse("T16 registers a THREE-LEVEL family; a registration claiming no triple is "
               "not this rung's")
    # The floors this file carries over must BE the registered ones.  Section 1
    # line 4 claims byte-identity; this turns the claim into a refusal.
    ctl = reg.get("controls", {})
    for name, got, want in (
            ("C_CONV", CONV_FLOOR, ctl.get("C_CONV", {}).get("floor")),
            ("C_PLAT", PLAT_FLOOR, ctl.get("C_PLAT", {}).get("floor")),
            ("C_MASS", MASS_FLOOR, ctl.get("C_MASS", {}).get("floor")),
            ("C_G", G_TOL, ctl.get("C_G", {}).get("floor")),
            ("W1_v", W1_FLOOR_V, ctl.get("W1", {}).get("floor_row_max_v")),
            ("W1_g", W1_FLOOR_G, ctl.get("W1", {}).get("floor_graded_reader")),
            ("W1_T", W1_FLOOR_T, ctl.get("W1", {}).get("floor_T"))):
        if want is None or got != want:
            refuse("carried-over floor %s is %r in this comparator and %r in the registration; "
                   "frozen document section 1 line 4 registers them BYTE-IDENTICAL"
                   % (name, got, want))
    return reg


# ------------------------------------------------------------ case identity
# CARRIED OVER BYTE-IDENTICALLY from analyse_t16.py:152-234, with ONE addition
# named at the bottom of case_identity().
def dict_value(path, key, vec=False):
    if not os.path.isfile(path):
        refuse("missing %s" % path)
    txt = open(path).read()
    if vec:
        m = re.search(r"^\s*%s\s+\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)\s*;" % key, txt, re.M)
        if not m:
            refuse("%s states no vector %s" % (path, key))
        return tuple(float(m.group(k)) for k in (1, 2, 3))
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, txt, re.M)
    if not m:
        refuse("%s states no %s" % (path, key))
    return float(m.group(1))


def patch_value(path, patch, key="value"):
    txt = open(path).read()
    m = re.search(r"^\s*%s\s*\{[^}]*?%s\s+uniform\s+([0-9.eE+-]+)\s*;" % (patch, key), txt, re.M | re.S)
    if not m:
        refuse("%s: no `%s uniform` for patch %s" % (path, key, patch))
    return float(m.group(1))


def patch_vector(path, patch, key="value"):
    txt = open(path).read()
    m = re.search(r"^\s*%s\s*\{[^}]*?%s\s+uniform\s+\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)\s*;"
                  % (patch, key), txt, re.M | re.S)
    if not m:
        refuse("%s: no `%s uniform (...)` for patch %s" % (path, key, patch))
    return tuple(float(m.group(k)) for k in (1, 2, 3))


def case_identity(case_dir, reg):
    """Every constant the grade depends on, READ FROM THE CASE'S OWN FILES and
    printed BEFORE any comparison (L-331: state the operands first)."""
    bmd = open(os.path.join(case_dir, "system", "blockMeshDict")).read()
    mv = re.search(r"vertices\s*\(\s*\(0 0 0\)\s*\(([0-9.eE+-]+) 0 0\)\s*\(([0-9.eE+-]+)\s+([0-9.eE+-]+) 0\)", bmd)
    mb = re.search(r"hex\s*\([^)]*\)\s*\(\s*(\d+)\s+(\d+)\s+1\s*\)", bmd)
    if not mv or not mb:
        refuse("%s: blockMeshDict does not carry the registered single-block form" % case_dir)
    b = float(mv.group(1))
    H = float(mv.group(3))
    N, Ny = int(mb.group(1)), int(mb.group(2))
    tp = os.path.join(case_dir, "constant", "transportProperties")
    ident = dict(case=os.path.basename(case_dir), b=b, H=H, N=N, Ny=Ny, dx=b / N, dy=H / Ny,
                 nu=dict_value(tp, "nu"), Pr=dict_value(tp, "Pr"), beta=dict_value(tp, "beta"),
                 TRef=dict_value(tp, "TRef"),
                 g=-dict_value(os.path.join(case_dir, "constant", "g"), "value", vec=True)[1])
    t0 = os.path.join(case_dir, "0.orig", "T")
    u0f = os.path.join(case_dir, "0.orig", "U")
    ident["T_hot"] = patch_value(t0, "hot")
    ident["T_cold"] = patch_value(t0, "cold")
    ident["dT"] = ident["T_hot"] - ident["T_cold"]
    ident["U0"] = patch_vector(u0f, "inlet")[1]
    ident["Re"] = ident["U0"] * b / ident["nu"]
    ident["G_mix"] = ident["g"] * ident["beta"] * ident["dT"] * b * b / (ident["nu"] * ident["U0"])
    ident["endTime"] = dict_value(os.path.join(case_dir, "system", "controlDict"), "endTime")
    ident["writeInterval"] = dict_value(os.path.join(case_dir, "system", "controlDict"), "writeInterval")
    ph = reg["physics"]
    if abs(ident["G_mix"] - ph["G_mix"]) > G_TOL:
        refuse("%s: G = Gr/Re recomputed from the case files is %.12g, not the registered %.12g"
               % (ident["case"], ident["G_mix"], ph["G_mix"]))
    if not ident["G_mix"] < EX.G_REVERSAL:
        refuse("%s: G = %.12g is at or past the DERIVED reversal threshold %g; this rung "
               "registered an unreversed profile" % (ident["case"], ident["G_mix"], EX.G_REVERSAL))
    if abs(ident["Re"] - ph["Re"]) > 1e-9:
        refuse("%s: Re recomputed from the case files is %.12g, not the registered %.12g"
               % (ident["case"], ident["Re"], ph["Re"]))
    if abs(ident["TRef"] - ident["T_cold"]) > 1e-9:
        refuse("%s: TRef %.17g is not the COLD wall temperature %.17g -- the referent's theta is "
               "(T - T_c)/dT and the Boussinesq reference must be the same datum"
               % (ident["case"], ident["TRef"], ident["T_cold"]))
    if Ny != ph["aspect"] * N:
        refuse("%s: Ny=%d is not aspect(%d) x N(%d); the cells are registered SQUARE"
               % (ident["case"], Ny, ph["aspect"], N))
    ident["j_station"] = int(ph["station_gaps"]) * N
    ident["witness_rows"] = [(k, ident["j_station"] + k * N) for k in ph["witness_gaps"]]
    for k, j in ident["witness_rows"]:
        if not 0 <= j < Ny:
            refuse("%s: witness row %+d b maps to index %d, outside the mesh" % (ident["case"], k, j))
    if not 0 <= ident["j_station"] < Ny:
        refuse("%s: station row index %d is outside the mesh" % (ident["case"], ident["j_station"]))
    # THE ONE ADDITION.  The station rule of section 4 fixes its CANDIDATE SET by
    # a FORMULA over the REGISTERED witness offsets, "not as a list, so it is
    # level-independent".  The offsets therefore have to travel as offsets.
    ident["witness_gaps"] = [int(k) for k in ph["witness_gaps"]]
    return ident


def latest_times(case_dir, n=2):
    ts = [t for t in os.listdir(case_dir) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", t) and float(t) > 0]
    ts = sorted(ts, key=float)
    return ts[-n:] if len(ts) >= n else None


# ---------------------------------- (i) STRICT COMPLETION, standing rule 4
def strict_completion(case_dir, root, case, ident, reg):
    """STANDING RULE 4, all of it, INCLUDING THE AGE GUARD.  Every conjunct's
    field list comes from the PINNED registration's `completion.needed_fields`;
    this function invents no list of its own.  A run is done only if ALL hold:
    rc = 0; an `End` line; last time == endTime; fields present; ExecutionTime
    count == endTime; and every field at endTime NEWER than the case's own
    `0/T` -- `0/T` is touched last at launch and so dates the run that was
    allowed to produce the answer.

    DISCLOSED DEPARTURE FROM THE PREDECESSOR, and the supervisor must rule on
    it: `analyse_t16.py:541-544` checks only the DONE marker and defers to
    `mark_done_t16.py`.  The frozen document section 1 line 7 (i) says "strict
    completion (rule 4) -- unchanged", which can be read as "the clause is not
    a T16c repair target" or as "do exactly what T16's comparator did".  This
    implementation reads it the first way and VERIFIES rule 4 here as well,
    because rule 4 is a standing rule and says comparators refuse rather than
    degrade.  NO THRESHOLD MOVES: every number is the registration's or rule
    4's own text.  It can only ever REFUSE where T16 would have graded, never
    the reverse, and it is named in T16c_INSTRUMENT_DIFFS.txt as a difference.
    """
    out = dict(case=case)
    done = os.path.join(root, "DONE.%s" % case)
    if not os.path.isfile(done):
        refuse("no DONE.%s -- the whole rung is graded or none of it is. Run mark_done_t16.py; "
               "if it says NOT DONE, that is the answer and this comparator does not overrule "
               "it." % case)
    status = os.path.join(root, "STATUS.%s" % case)
    if not os.path.isfile(status):
        refuse("%s: DONE marker with no STATUS.%s -- rule 4 needs rc" % (case, case))
    st = open(status).read()
    mrc = re.search(r"^rc\s*=\s*(-?\d+)\s*$", st, re.M)
    if not mrc:
        refuse("%s: STATUS carries no `rc =` line; rule 4's first conjunct cannot be read" % case)
    out["rc"] = int(mrc.group(1))
    if out["rc"] != 0:
        refuse("%s: rc = %d, not 0 (rule 4)" % (case, out["rc"]))
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        refuse("%s: no log.solve; rule 4 needs the End line and the ExecutionTime count" % case)
    txt = open(log, errors="replace").read()
    out["end_line"] = bool(re.search(r"^End\s*$", txt, re.M))
    if not out["end_line"]:
        refuse("%s: log.solve carries no `End` line (rule 4)" % case)
    out["execution_time_count"] = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    et = int(round(ident["endTime"]))
    if out["execution_time_count"] != et:
        refuse("%s: %d ExecutionTime lines, endTime is %d (rule 4: the count must equal endTime)"
               % (case, out["execution_time_count"], et))
    ts = latest_times(case_dir, 2)
    if ts is None:
        refuse("%s has fewer than two written times beyond 0" % case)
    out["times"] = ts
    if abs(float(ts[-1]) - ident["endTime"]) > 1e-9:
        refuse("%s: latest time %s is not endTime %g (rule 4)" % (case, ts[-1], ident["endTime"]))
    needed = reg.get("completion", {}).get("needed_fields")
    if not needed:
        refuse("the pinned registration carries no completion.needed_fields; rule 4's field list "
               "is REGISTERED and this comparator will not invent one")
    out["needed_fields"] = list(needed)
    t0T = os.path.join(case_dir, "0", "T")
    if not os.path.isfile(t0T):
        refuse("%s: no 0/T -- the AGE GUARD has no datum, and a guard with no datum is not a "
               "guard (rule 4)" % case)
    age0 = os.path.getmtime(t0T)
    out["age_datum_mtime"] = age0
    ages = {}
    for f in needed:
        p = os.path.join(case_dir, ts[-1], f)
        if not os.path.isfile(p):
            refuse("%s: registered field %s absent at endTime %s (rule 4)" % (case, f, ts[-1]))
        ages[f] = os.path.getmtime(p) - age0
        if ages[f] <= 0.0:
            refuse("%s: AGE GUARD -- %s at endTime %s is %.3f s OLDER than the case's own 0/T. "
                   "0/T is touched last at launch, so it dates the run allowed to produce this "
                   "answer; a field older than it was not written by that run (rule 4)"
                   % (case, f, ts[-1], -ages[f]))
    out["field_age_s"] = ages
    out["ok"] = True
    return out


# ------------------------------------------------------------- THE READERS
# CARRIED OVER BYTE-IDENTICALLY from analyse_t16.py:244-284.
def locate_internal(lines):
    """(first value line index, count) located STRUCTURALLY."""
    for i, ln in enumerate(lines):
        if "internalField" in ln and "nonuniform" in ln:
            for j in range(i, min(i + 5, len(lines))):
                if lines[j].strip() == "(":
                    cnt = None
                    for k in range(i, j + 1):
                        mc = re.search(r"\b(\d+)\s*$", lines[k].strip())
                        if mc:
                            cnt = int(mc.group(1))
                    return j + 1, cnt
            return None, None
    return None, None


def read_field(case_dir, time, name, vector=False):
    """THE PRODUCTION READER for scalar and vector internalFields.  Every graded
    number and every planted control goes through this function."""
    p = os.path.join(case_dir, str(time), name)
    if not os.path.isfile(p):
        refuse("no %s at time %s in %s -- a missing number is not a zero" % (name, time, case_dir))
    lines = open(p).read().splitlines()
    start, cnt = locate_internal(lines)
    if start is None:
        if re.search(r"internalField\s+uniform", "\n".join(lines[:40])):
            refuse("%s at time %s is UNIFORM -- the solver wrote no solution into it" % (name, time))
        refuse("could not locate the internalField of %s STRUCTURALLY" % p)
    if cnt is None:
        refuse("%s: no element count before the list" % p)
    vals = []
    for k in range(start, start + cnt):
        s = lines[k].strip()
        if vector:
            m = re.fullmatch(r"\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)", s)
            if not m:
                refuse("%s line %d is not a vector: %r" % (p, k + 1, s))
            vals.append((float(m.group(1)), float(m.group(2)), float(m.group(3))))
        else:
            vals.append(float(s))
    return vals


def row_of(vals, N, j):
    return vals[j * N:(j + 1) * N]


def y_centres(N):
    return [(i + 0.5) / N for i in range(N)]


def y_over_b(j, N):
    """The PHYSICAL streamwise coordinate of row j, in units of b.  The cells are
    registered SQUARE (dy = dx = b/N, checked in case_identity), so row j sits at
    (j + 0.5)/N.  This is `analyse_t16.py:307`'s `row_y_over_b`, promoted to a
    function because section 4 maps the station BETWEEN LEVELS by y/b."""
    return (j + 0.5) / N


def row_at_y(y, N, Ny):
    """The row whose CENTRE is nearest y (in units of b).

    DISCLOSED: the frozen document section 4 says the station is applied to the
    coarse and medium levels "by physical coordinate y/b, not by index" and does
    NOT say how a y/b that falls between two centres is resolved.  EXACT
    coincidence is IMPOSSIBLE at r = 2 and this is arithmetic, not opinion: a
    fine centre is (j + 0.5)/N_f, a coarse centre is (i + 0.5)/(N_f/2), and
    equating them gives j = 2i + 0.5, never an integer.  NEAREST CENTRE is the
    reading implemented; the residual |y_level - y_selected| is MEASURED and
    PRINTED for every level so a reader can see how far the mapping moved."""
    j = int(math.floor(y * N))
    best, bj = None, 0
    for cand in (j - 1, j, j + 1):
        if 0 <= cand < Ny:
            d = abs(y_over_b(cand, N) - y)
            if best is None or d < best:
                best, bj = d, cand
    return bj, best


def readers(case_dir, time, ident, j_row=None):
    """All graded quantities and witnesses at ONE ROW, from disk.

    CARRIED OVER from analyse_t16.py:295-355 with exactly one change: the row is
    a PARAMETER.  With `j_row=None` this is byte-for-byte T16's behaviour at the
    registered station, INCLUDING its witness rows, because T16's
    `ident["witness_rows"]` is `[(k, j_station + k*N)]`.  With `j_row=j` it is
    section 4's `W1_T(j)` metric and the graded readers at the selected station:
    the SAME reader at another row, which is what section 4 registers ("T16's
    OWN streamwise temperature-development witness ... Not a new metric")."""
    N, Ny = ident["N"], ident["Ny"]
    j0 = ident["j_station"] if j_row is None else int(j_row)
    if not 0 <= j0 < Ny:
        refuse("%s: row index %d is outside the mesh" % (ident["case"], j0))
    wit = [(k, j0 + k * N) for k in ident["witness_gaps"]]
    for k, j in wit:
        if not 0 <= j < Ny:
            refuse("%s: witness row %+d b about row %d maps to index %d, outside the mesh"
                   % (ident["case"], k, j0, j))
    U = read_field(case_dir, time, "U", vector=True)
    T = read_field(case_dir, time, "T")
    if len(U) != N * Ny or len(T) != N * Ny:
        refuse("%s at time %s: %d U / %d T cells, mesh has %d"
               % (ident["case"], time, len(U), len(T), N * Ny))
    Y = y_centres(N)
    U0, dT = ident["U0"], ident["dT"]
    vrow = [u[1] / U0 for u in row_of(U, N, j0)]
    trow = row_of(T, N, j0)
    out = dict(time=str(time), row_index=j0, row_y_over_b=y_over_b(j0, N))
    out["G1"] = EX.lagrange4(Y, vrow, EX.Y_STAR)
    out["G1b"] = EX.cubic_max_location(Y, vrow)
    half = 0.5 * ident["dx"]
    out["tau_hot"] = (vrow[0] - 0.0) / half
    out["tau_cold"] = (vrow[-1] - 0.0) / half
    out["G3"] = out["tau_hot"] / out["tau_cold"] if out["tau_cold"] != 0.0 else float("inf")
    tlin = [ident["T_hot"] - dT * y for y in Y]
    out["G2"] = math.sqrt(sum(((t - tl) / dT) ** 2 for t, tl in zip(trow, tlin)) / N)
    out["mass_mean"] = sum(vrow) / N
    out["mass_dev"] = abs(out["mass_mean"] - 1.0)
    out["v_min"] = min(vrow)
    out["reversed_cells"] = sum(1 for v in vrow if v <= 0.0)
    ym = sum(Y) / N
    tm = sum(trow) / N
    slope = sum((y - ym) * (t - tm) for y, t in zip(Y, trow)) / sum((y - ym) ** 2 for y in Y)
    out["T_slope_rel"] = (slope / (-dT)) - 1.0
    out["T_monotone"] = all(trow[i] > trow[i + 1] for i in range(N - 1))

    def rowdiff(j):
        vr = [u[1] / U0 for u in row_of(U, N, j)]
        tr = row_of(T, N, j)
        return (max(abs(a - b) for a, b in zip(vr, vrow)),
                abs(EX.lagrange4(Y, vr, EX.Y_STAR) - out["G1"]) / abs(out["G1"]),
                max(abs(a - b) for a, b in zip(tr, trow)) / dT)

    w1 = {}
    for k, j in wit:
        w1["%+db" % k] = dict(zip(("v", "g", "T"), rowdiff(j)))
    out["W1"] = w1
    out["W1_v_max"] = max(d["v"] for d in w1.values())
    out["W1_g_max"] = max(d["g"] for d in w1.values())
    out["W1_T_max"] = max(d["T"] for d in w1.values())
    out["W1_max"] = max(out["W1_v_max"], out["W1_g_max"], out["W1_T_max"])
    return out


# ------------------------------- (iv) THE STATION RULE, frozen document sec. 4
def candidate_rows(N, Ny, gaps):
    """SECTION 4 CANDIDATE SET, frozen AS THE FORMULA and not as a list, "so it
    is level-independent": every interior row j for which ALL registered witness
    offsets lie inside the domain."""
    return [j for j in range(Ny) if all(0 <= j + k * N < Ny for k in gaps)]


def w1_T_at(Tvals, N, Ny, dT, gaps, j):
    """SECTION 4's METRIC, computed for one row.

        W1_T(j) = max over the registered witness offsets k of
                  max_i |T(row j + kN)_i - T(row j)_i| / dT

    This is the T-limb of `readers()`'s `rowdiff` (`analyse_t16.py:340-354`),
    extracted so a scan over every candidate row does not also pay for the
    Lagrange, the cubic and the shear ratio.  IT IS ADMITTED ONLY BECAUSE IT IS
    SHOWN EQUAL TO THE FROZEN READER: `station_metric_agreement()` compares the
    two at three rows on every level and REFUSES on any disagreement, and a
    mutation control reddens exactly that limb."""
    base = Tvals[j * N:(j + 1) * N]
    m = 0.0
    for k in gaps:
        jj = j + k * N
        if not 0 <= jj < Ny:
            refuse("W1_T(%d): witness offset %+d leaves the domain -- j was not in the candidate "
                   "set, and section 4's candidate set is the formula that prevents this" % (j, k))
        row = Tvals[jj * N:(jj + 1) * N]
        for a, b in zip(row, base):
            d = abs(a - b)
            if d > m:
                m = d
    return m / dT


def station_metric_agreement(case_dir, time, ident, Tvals, rows):
    """The fast scanner IS the frozen reader, measured at `rows` rather than
    asserted.  REFUSES on any disagreement."""
    N, Ny, dT, gaps = ident["N"], ident["Ny"], ident["dT"], ident["witness_gaps"]
    checked = {}
    for j in rows:
        fast = w1_T_at(Tvals, N, Ny, dT, gaps, j)
        slow = readers(case_dir, time, ident, j_row=j)["W1_T_max"]
        if fast != slow:
            refuse("station metric disagreement at row %d of %s: the fast scanner returns %.17g "
                   "and the FROZEN reader returns %.17g. Section 4 registers T16's OWN witness "
                   "and NOT a new metric, so a scanner that is not that witness is not admitted."
                   % (j, ident["case"], fast, slow))
        checked[j] = fast
    return checked


def select_station(Tvals_f, ident_f, cand_f):
    """SECTION 4 SELECTION: the smallest j in the candidate set satisfying
    W1_T(j) <= 1.0e-06 ON THE FINE LEVEL.  TIE-BREAK: none is possible -- the
    scan is strictly inlet-to-outlet and "smallest j" is unique.  Stated because
    section 4 states it: a rule with an unreachable tie-break clause invites one
    to be invented later."""
    N, Ny, dT, gaps = ident_f["N"], ident_f["Ny"], ident_f["dT"], ident_f["witness_gaps"]
    scan = []
    chosen = None
    for j in cand_f:
        w = w1_T_at(Tvals_f, N, Ny, dT, gaps, j)
        scan.append((j, w))
        if chosen is None and w <= STATION_FLOOR_T:
            chosen = j
    return chosen, scan


# ------------------------------------------------- iterative convergence
# CARRIED OVER BYTE-IDENTICALLY from analyse_t16.py:359-403.
def residual_history(case_dir):
    log = os.path.join(case_dir, "log.solve")
    if not os.path.isfile(log):
        return None, "no log.solve"
    hist = []
    cur = None
    with open(log, errors="replace") as fh:
        for line in fh:
            mt = re.match(r"^Time = ([0-9.eE+-]+)\s*$", line)
            if mt:
                cur = dict(it=float(mt.group(1)))
                hist.append(cur)
                continue
            if cur is None:
                continue
            ms = re.search(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", line)
            if ms and ms.group(1) not in cur:
                cur[ms.group(1)] = float(ms.group(2))
    if not hist:
        return None, "no `Time =` lines in log.solve"
    return hist, ""


def iterative_convergence(case_dir, end_time):
    hist, why = residual_history(case_dir)
    if hist is None:
        return dict(ok=False, why=why)
    n = len(hist)
    tail = [h for h in hist if h["it"] > 0.9 * end_time]
    if not tail:
        return dict(ok=False, why="no iterations in the final 10 percent of endTime")
    worst = {}
    for f in ("Ux", "Uy", "T", "p_rgh"):
        vals = [h[f] for h in tail if f in h]
        worst[f] = max(vals) if vals else None
    gated = ("Uy", "T", "p_rgh")
    missing = [f for f in gated if worst[f] is None]
    if missing:
        return dict(ok=False, why="no residual lines for %s in the final 10 percent" % ",".join(missing),
                    worst=worst)
    bad = [f for f in gated if worst[f] > CONV_FLOOR]
    return dict(ok=not bad, worst=worst, n_iterations=n, window=len(tail),
                why=("initial residual of %s above %.0e in the final 10 percent"
                     % (",".join(bad), CONV_FLOOR)) if bad else "",
                Ux_reported_not_gated=worst["Ux"])


# ------------------------------------------------- planted-zero controls
# `plant` and `planted_zero_controls` are CARRIED OVER BYTE-IDENTICALLY from
# analyse_t16.py:407-498 (frozen document section 6 carries C_PZ), with the
# single change that the readers are taken at the GRADED station rather than at
# the registered one -- the control has to sit on the row the verdict uses.
def plant(case_copy, time, name, indices, deltas, vector_component=None):
    """Add deltas[k] to indices[k] IN PLACE, located STRUCTURALLY.  `deltas` is a
    list the same length as `indices`, so a plant can ALTERNATE IN SIGN -- the
    shape an RMS reader can see whatever it measures about (L-340)."""
    p = os.path.join(case_copy, str(time), name)
    lines = open(p).read().splitlines(True)
    start, cnt = locate_internal(lines)
    if start is None:
        refuse("plant: could not locate internalField of %s" % p)
    for idx, delta in zip(indices, deltas):
        ln = lines[start + idx]
        if vector_component is None:
            lines[start + idx] = "%.17g\n" % (float(ln.strip()) + delta)
        else:
            m = re.fullmatch(r"\(\s*([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*\)", ln.strip())
            if not m:
                refuse("plant: line %d of %s is not a vector" % (start + idx + 1, p))
            v = [float(m.group(k)) for k in (1, 2, 3)]
            v[vector_component] += delta
            lines[start + idx] = "(%.17g %.17g %.17g)\n" % tuple(v)
    open(p, "w").write("".join(lines))
    return start + indices[0] + 1


def _scratch_copy(tmp, case_dir, time):
    dst = os.path.join(tmp, os.path.basename(case_dir))
    os.makedirs(dst)
    for sub in ("system", "constant", "0.orig"):
        shutil.copytree(os.path.join(case_dir, sub), os.path.join(dst, sub), symlinks=True)
    shutil.copytree(os.path.join(case_dir, str(time)), os.path.join(dst, str(time)))
    if os.path.realpath(dst).startswith(os.path.realpath(case_dir)):
        refuse("planted-zero control: scratch copy resolved INSIDE the case tree")
    return dst


def planted_zero_controls(case_dir, time, ident, j_graded, read=readers):
    """Both arms for EVERY reader, each plant sized AND SHAPED to ITS reader
    (rule 3, L-340).  G1 / G1b / G3 / W1 are point readers and get a point plant.
    G2 is an RMS over the whole row and gets an ALL-ROW ALTERNATING-SIGN plant."""
    N = ident["N"]
    j0 = j_graded
    Y = y_centres(N)
    i_star = min(range(N), key=lambda i: abs(Y[i] - EX.Y_STAR))
    i_peak = min(range(N), key=lambda i: abs(Y[i] - EX.Y_MAX))
    j_wit = j0 + ident["witness_gaps"][0] * N
    tmp = tempfile.mkdtemp(prefix="t16cpz_")
    try:
        dst = _scratch_copy(tmp, case_dir, time)
        base = read(dst, time, ident, j_row=j0)
        again = read(dst, time, ident, j_row=j0)
        for key in ("G1", "G1b", "G2", "G3", "W1_max"):
            if again[key] != base[key]:
                refuse("planted-zero NEGATIVE ARM FAILED on %s: identical bytes read back "
                       "%.17g then %.17g. The reader is NOISY; every T16c number depending on "
                       "it is withdrawn, not re-graded." % (key, base[key], again[key]))
        row = [i + N * j0 for i in range(N)]
        alt = [1.0 if i % 2 == 0 else -1.0 for i in range(N)]
        specs = [  # (reader key, field, indices, signs, component, scale)
            ("G1", "U", [i_star + N * j0], [1.0], 1, ident["U0"]),
            ("G1b", "U", [i_peak + N * j0], [1.0], 1, ident["U0"]),
            ("G2", "T", row, alt, None, ident["dT"]),        # ALL-ROW ALTERNATING (L-340)
            ("G3", "U", [0 + N * j0], [1.0], 1, ident["U0"]),
            ("W1_max", "U", [i_star + N * j_wit], [1.0], 1, ident["U0"]),
        ]
        report = {}
        for key, field, idxs, signs, comp, scale in specs:
            seen, floor = {}, None
            for mag in (1.0, 1e-1, 1e-2, PLANT_REL, 1e-4, 1e-5, 1e-6, 1e-7):
                shutil.copy2(os.path.join(case_dir, str(time), field),
                             os.path.join(dst, str(time), field))
                line = plant(dst, time, field, idxs, [s * mag * scale for s in signs], comp)
                got = read(dst, time, ident, j_row=j0)
                d = abs(got[key] - base[key])
                seen["%g" % mag] = d
                if d > 0.0:
                    floor = mag
            shutil.copy2(os.path.join(case_dir, str(time), field),
                         os.path.join(dst, str(time), field))
            if floor is None:
                refuse("planted-zero POSITIVE ARM FAILED for reader %s: no plant magnitude was "
                       "visible (field %s, %d cell(s) from line %d). The reader is BLIND and every "
                       "zero it has produced is worthless." % (key, field, len(idxs), line))
            if seen["%g" % PLANT_REL] == 0.0:
                refuse("planted-zero POSITIVE ARM FAILED for reader %s at the REGISTERED plant "
                       "%.4g x scale: invisible while %.4g x scale WAS visible"
                       % (key, PLANT_REL, floor))
            report[key] = dict(status="PASS", field=field, cells_planted=len(idxs), first_line=line,
                               shape=("ALL-ROW ALTERNATING SIGN" if len(idxs) > 1 else "POINT"),
                               plant=PLANT_REL * scale, recovered=seen["%g" % PLANT_REL],
                               demonstrated_detection_floor=floor, ladder=seen)
        return report
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def station_metric_planted_control(case_dir, time, ident, j, read_T=None):
    """RULE 3 FOR THE NEW READER.  `w1_T_at` decides WHERE the rung is graded; a
    blind one would select the first candidate row whatever the field said, and
    every "the temperature is developed here" would be worthless.

    THE PREDICATE IS THE FAMILY'S RELATIVE FORM -- pesweep:141, dts:594,
    dts_p:226 -- and NOT analyse_t3.py:327's `seen >= PLANT - 1e-15`; the
    docstring of this module measures why, and this function PRINTS the two ULP
    ratios so the reason is a reading rather than a recollection.

    THE PLANT GOES INTO THE GLOBAL ARGMAX CELL, with the SIGN that ADDS to the
    difference already there, and the acceptance is on the RECOVERED DELTA:

        delta = got - base,  PLANT*(1-1e-9) <= delta <= PLANT*(1+1e-9) + 1e-12

    Both halves of that are load-bearing and neither is decoration.
      * THE CELL AND SIGN.  Plant into a cell whose existing difference has the
        opposite sign and the reader returns |d| - PLANT, which is below
        PLANT*(1-1e-9) for any real |d|; the control would then RED on a
        perfectly good reader.  Plant into a cell that is not the argmax and the
        maximum may not move at all.  The choice is a property of the CONTROL
        and is disclosed here because a control that quietly picks a favourable
        cell would be worthless.  At the global argmax with an additive sign,
        got = base + PLANT EXACTLY, so the two-sided window is arithmetic.
      * THE DELTA, NOT THE VALUE.  `got >= PLANT` alone is passed by a BLIND
        reader whenever the real signal already exceeds the plant -- which is
        precisely the developing-region rows where this reader decides things.
        The family's form at pesweep:141 carries that hole because there the
        real signal is small; here it is not, so the control is taken on the
        MOVEMENT.  L26 drives a blind reader against this predicate and shows
        it red."""
    N, Ny, dT, gaps = ident["N"], ident["Ny"], ident["dT"], ident["witness_gaps"]
    reader = read_T if read_T is not None else (
        lambda cd, t: read_field(cd, t, "T"))
    tmp = tempfile.mkdtemp(prefix="t16cst_")
    try:
        dst = _scratch_copy(tmp, case_dir, time)
        Tv = reader(dst, time)
        Tv2 = reader(dst, time)
        if Tv != Tv2:
            refuse("station-metric NEGATIVE ARM FAILED: identical bytes read back differently. "
                   "The T reader is NOISY and every station this rung selects is worthless.")
        base = w1_T_at(Tv, N, Ny, dT, gaps, j)
        # the GLOBAL argmax cell over every registered witness offset
        best = None
        for k in gaps:
            jj = j + k * N
            for i in range(N):
                d = Tv[jj * N + i] - Tv[j * N + i]
                if best is None or abs(d) > abs(best[2]):
                    best = (jj, i, d)
        jj, i_cell, d_cell = best
        sign = 1.0 if d_cell >= 0.0 else -1.0
        idx = jj * N + i_cell
        line = plant(dst, time, "T", [idx], [sign * PLANT_REL * dT], None)
        Tp = reader(dst, time)
        got = w1_T_at(Tp, N, Ny, dT, gaps, j)
        delta = got - base
        lo_ok = delta >= PLANT_REL * (1.0 - 1e-9)
        hi_ok = delta <= PLANT_REL * (1.0 + 1e-9) + 1e-12
        ulp = math.ulp(float(ident["T_hot"]))
        rec = dict(status="PASS" if (lo_ok and hi_ok) else "FAIL",
                   row=j, witness_row=jj, cell=i_cell, sign=sign, line=line,
                   base=base, plant=PLANT_REL, got=got, delta=delta,
                   acceptance="PLANT*(1-1e-9) <= (got - base) <= PLANT*(1+1e-9) + 1e-12",
                   predicate_source="the RELATIVE form at T1_runs/analyse_pesweep.py:141, "
                                    "analyse_dts.py:594, analyse_dts_p.py:226",
                   rejected_predicate="analyse_t3.py:327 `seen >= PLANT - 1e-15`",
                   ulp_at_T_hot=ulp,
                   t3_slack_in_ulp=1e-15 / ulp,
                   chosen_slack_in_ulp=(PLANT_REL * 1e-9) / ulp)
        if not (lo_ok and hi_ok):
            refuse("station-metric POSITIVE ARM FAILED at row %d: planted %.6e (relative) into "
                   "cell %d of witness row %d at line %d, base %.6e, reader returned %.6e, so the "
                   "recovered delta is %.6e; acceptance is %s. The station reader cannot see a "
                   "plant it must see, so every station it selects is worthless."
                   % (j, PLANT_REL, i_cell, jj, line, base, got, delta, rec["acceptance"]))
        return rec
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------- rule 5: the gate
# CARRIED OVER BYTE-IDENTICALLY from analyse_t16.py:502-535.
def triple_of(vals):
    """roache_triple.gci_equal on (c, m, f) at r = 2, dim = 2."""
    return gci_equal(vals["c"], vals["m"], vals["f"], REFINEMENT, DIM, fs=FS)


def band_verdict(value, lo, hi):
    return "PASS" if lo <= value <= hi else "GATE FAIL"


def apply_gate(value, lo, hi, tr, gate1_ok, gate1_why, exact_class=False):
    """The ONLY function that writes a verdict.  Rule 5's fixed order:
    (1) any level not converged / not plateaued / not developed / not carrying
        the registered mean, or a station clause failing -> NOT A RESULT;
    (2) triple not CONVERGING -> NOT A RESULT (EXACT-class rows skip (2): their
        floor is the verdict and the triple state is printed beside it);
    (3) the band.  The band verdict is computed FIRST and the final verdict is
    either it or NOT A RESULT -- the gate is one-way."""
    bv = band_verdict(value, lo, hi)
    if not gate1_ok:
        return "NOT A RESULT", bv, "gate (1): " + gate1_why
    if not exact_class and tr["state"] != "CONVERGING":
        p = tr.get("order")
        return ("NOT A RESULT", bv,
                "gate (2): triple is %s%s -- rule 5 makes a triple that is not CONVERGING NOT A "
                "RESULT whatever its value says (STAGNANT_FLOOR=%g, P_MIN=%g)"
                % (tr["state"], (" (p = %.3e)" % p) if p is not None else "", STAGNANT_FLOOR, P_MIN))
    return bv, bv, ""


def fmt_tr(tr):
    """Rule 5: NEVER quote a GCI when the three values are not monotone.
    `gci_equal` returns GCI_pct only in the CONVERGING branch, which is reached
    only when e32/e21 > 0 -- i.e. only on a monotone triple.  The monotone flag
    is PRINTED beside the state so that invariant is visible rather than
    trusted, and a selftest limb drives every non-monotone shape to check that
    GCI is absent."""
    p = tr.get("order")
    g = tr.get("GCI_pct")
    return "%s mono=%s p=%s GCI=%s" % (tr["state"], monotone(tr),
                                       ("%.4f" % p) if p is not None else "n/a",
                                       ("%.4e%%" % g) if g is not None else "REFUSED")


# ---------------------------------------------------------------- the grade
def grade(root, json_out, reg):
    """THE REGISTERED ORDER OF CRITERIA, frozen document section 1 line 7."""
    _station_floor_identity_check()
    root = os.path.abspath(root)
    print("T16c comparator.  Frozen authority: docs/campaigns/T-family/T16c_PREREGISTRATION.md")
    print("  pinned instrument %s sha256 %s" % (os.path.basename(REG_PATH), REG_SHA256))
    prov = {}
    for p, w in ((EXACT_PATH, "exact_t16.py"), (BUILD_PATH, "build_t16.py"),
                 (T16_PATH, "analyse_t16.py")):
        prov[w] = sha256_of(p)
        print("  provenance (REPORTED, not gated on the grading path) %-16s sha256 %s" % (w, prov[w]))

    # ---- (i) STRICT COMPLETION, rule 4, including the age guard --------------
    print("(i) strict completion, standing rule 4 (rc, End, last time == endTime, fields present, "
          "ExecutionTime count == endTime, AGE GUARD against the case's own 0/T):")
    idents, times, comp = {}, {}, {}
    for lv in LEVELS:
        case = CASES[lv]
        d = os.path.join(root, case)
        ident = case_identity(d, reg)
        c = strict_completion(d, root, case, ident, reg)
        idents[lv], times[lv], comp[lv] = ident, c["times"], c
        print("    %s rc=%d End=%s ExecutionTime lines=%d == endTime=%d, fields %s all NEWER than "
              "0/T by %s s" % (case, c["rc"], c["end_line"], c["execution_time_count"],
                               int(round(ident["endTime"])), ",".join(c["needed_fields"]),
                               {k: "%.0f" % v for k, v in c["field_age_s"].items()}))

    print("verifying the DERIVED analytic reference before any comparison:")
    r, f = EX.verify()
    if f:
        refuse("the referent's Route B does not verify: %s" % "; ".join(f))
    EX.selfcheck_readers()
    print("operands (L-331), read from each case's own files:")
    for lv in LEVELS:
        ident = idents[lv]
        print("  %s: N=%d Ny=%d dx=%.4e nu=%.4e Pr=%.4g beta=%.6e TRef=%.4f T_hot=%.10f "
              "T_cold=%.10f g=%.3f U0=%.10f Re=%.8f G=Gr/Re=%.10f (reversal %g, margin %.4f) "
              "REGISTERED station row %d at y/b=%.4f times=%s"
              % (ident["case"], ident["N"], ident["Ny"], ident["dx"], ident["nu"], ident["Pr"],
                 ident["beta"], ident["TRef"], ident["T_hot"], ident["T_cold"], ident["g"],
                 ident["U0"], ident["Re"], ident["G_mix"], EX.G_REVERSAL,
                 EX.G_REVERSAL / ident["G_mix"], ident["j_station"],
                 y_over_b(ident["j_station"], ident["N"]), times[lv]))

    # ---- (ii) THE WITNESSES, ALL THREE LEVELS, BEFORE ANY GUARD -------------
    # Frozen document section 3.  In T16 this ran NINE LINES BELOW the guard that
    # refused, so verification's entire diagnosis was unreachable exactly when it
    # was needed (D576's shape).  It runs FIRST here, over ALL THREE LEVELS, and
    # is REPORTED UNCONDITIONALLY -- including on a run that refuses at (iii).
    print("(ii) W1 DEVELOPMENT WITNESSES at the REGISTERED station, ALL THREE LEVELS, REPORTED "
          "UNCONDITIONALLY AND BEFORE ANY GUARD (frozen document section 3):")
    reg_reads, prev_reads = {}, {}
    for lv in LEVELS:
        ident = idents[lv]
        d = os.path.join(root, CASES[lv])
        rr = readers(d, times[lv][-1], ident)
        reg_reads[lv] = rr
        print("    %s W1_v %.4e / %.0e   W1_g %.4e / %.0e   W1_T %.4e / %.0e   (%s)  "
              "T_slope_rel %+.4e  monotone %s"
              % (ident["case"], rr["W1_v_max"], W1_FLOOR_V, rr["W1_g_max"], W1_FLOOR_G,
                 rr["W1_T_max"], W1_FLOOR_T,
                 {k: "v %.1e g %.1e T %.1e" % (v["v"], v["g"], v["T"]) for k, v in rr["W1"].items()},
                 rr["T_slope_rel"], rr["T_monotone"]))

    # ---- (iii) C_TRANSPOSE -------------------------------------------------
    print("(iii) C_TRANSPOSE, the ORDERING guard, threshold %.1f (frozen document section 1 line "
          "4, sized to the %.1f signature and NOT to instrument precision):" % (C_TRANSPOSE_TOL,
                                                                               TRANSPOSE_SIGNATURE))
    ct = {}
    for lv in LEVELS:
        v = reg_reads[lv]["T_slope_rel"]
        ct[lv] = dict(value=v, ok=abs(v) <= C_TRANSPOSE_TOL,
                      margin_factor=(C_TRANSPOSE_TOL / abs(v)) if v != 0.0 else float("inf"))
        print("    %s |slope/(-dT) - 1| = %.4e, threshold %.1f -> %s (%.4g x inside)"
              % (CASES[lv], abs(v), C_TRANSPOSE_TOL, "ok" if ct[lv]["ok"] else "REFUSE",
                 ct[lv]["margin_factor"]))
    bad = [lv for lv in LEVELS if not ct[lv]["ok"]]
    if bad:
        refuse("C_TRANSPOSE -- the station row of %s carries NO hot-to-cold gradient: "
               "|slope/(-dT) - 1| = %s against a threshold of %.1f, and the signature of a read "
               "that walks an isothermal line is %.1f. THIS IS AN ORDERING-CLASS DEFECT AND THE "
               "CAUSE IS NOT NAMED HERE: a transposed (y-fastest) cell ordering, a uniform field "
               "and a field that is not the solution all produce it, and publishing ONE of them "
               "as the finding is the error T16c exists to repair."
               % (",".join(CASES[lv] for lv in bad),
                  ", ".join("%.4e" % abs(ct[lv]["value"]) for lv in bad),
                  C_TRANSPOSE_TOL, TRANSPOSE_SIGNATURE))

    # ---- (iv) STATION SELECTION, frozen document section 4 ------------------
    print("(iv) STATION SELECTION by the frozen RULE of section 4: metric W1_T(j) "
          "(analyse_t16.py:340-354, T16's OWN witness), threshold %.0e (W1_FLOOR_T, "
          "analyse_t16.py:116), SMALLEST j in the candidate set on the FINE level, then applied "
          "to c and m BY PHYSICAL COORDINATE y/b:" % STATION_FLOOR_T)
    Tvals = {}
    cands = {}
    for lv in LEVELS:
        d = os.path.join(root, CASES[lv])
        Tvals[lv] = read_field(d, times[lv][-1], "T")
        cands[lv] = candidate_rows(idents[lv]["N"], idents[lv]["Ny"], idents[lv]["witness_gaps"])
        if not cands[lv]:
            refuse("%s: section 4's candidate set is EMPTY -- no interior row has all registered "
                   "witness offsets inside the domain" % CASES[lv])
        probe = [cands[lv][0], cands[lv][len(cands[lv]) // 2], cands[lv][-1]]
        station_metric_agreement(os.path.join(root, CASES[lv]), times[lv][-1], idents[lv],
                                 Tvals[lv], probe)
        print("    %s candidate set: %d rows, j in [%d, %d] (y/b in [%.4f, %.4f]); the fast "
              "scanner was MEASURED EQUAL to the frozen reader at rows %s"
              % (CASES[lv], len(cands[lv]), cands[lv][0], cands[lv][-1],
                 y_over_b(cands[lv][0], idents[lv]["N"]), y_over_b(cands[lv][-1], idents[lv]["N"]),
                 probe))

    j_f, scan_f = select_station(Tvals["f"], idents["f"], cands["f"])
    station = dict(rule="frozen T16c_PREREGISTRATION.md section 4", floor=STATION_FLOOR_T,
                   candidate_counts={lv: len(cands[lv]) for lv in LEVELS})
    gate1_ok, gate1_why = True, []
    j_graded = {}
    if j_f is None:
        wmin = min(w for _, w in scan_f)
        jmin = min(scan_f, key=lambda t: t[1])[0]
        station.update(selected=None, reachable=False,
                       best_row=jmin, best_W1_T=wmin,
                       reason="THE UNREACHABLE BRANCH, registered in section 4")
        print("    UNREACHABLE BRANCH: NO j in the fine level's candidate set reaches W1_T <= "
              "%.0e. The best is row %d at W1_T = %.4e, which is %.4g x the floor."
              % (STATION_FLOOR_T, jmin, wmin, wmin / STATION_FLOOR_T))
        print("    Section 4, registered in advance and WITHOUT APPEAL: the station is NOT "
              "relocated, the threshold is NOT loosened, the candidate set is NOT widened. The "
              "recorded reason is that THE REGISTERED REFERENT DOES NOT DESCRIBE THIS SOLVE'S "
              "REGIME, and the honest consequence is that the CASE, not the comparator, needs "
              "changing.")
        gate1_ok = False
        gate1_why.append("section 4 unreachable branch: no candidate row reaches W1_T <= %.0e on "
                         "the fine level (best %.4e at row %d)" % (STATION_FLOOR_T, wmin, jmin))
    else:
        y_star = y_over_b(j_f, idents["f"]["N"])
        station.update(selected=True, reachable=True, fine_row=j_f, y_over_b=y_star,
                       fine_W1_T=w1_T_at(Tvals["f"], idents["f"]["N"], idents["f"]["Ny"],
                                         idents["f"]["dT"], idents["f"]["witness_gaps"], j_f))
        print("    SELECTED on the fine level: SMALLEST candidate j = %d, y/b = %.6f, "
              "W1_T = %.4e <= %.0e. TIE-BREAK: none possible (strict inlet-to-outlet scan)."
              % (j_f, y_star, station["fine_W1_T"], STATION_FLOOR_T))
        per = {}
        for lv in LEVELS:
            ident = idents[lv]
            if lv == "f":
                jj, resid = j_f, 0.0
            else:
                jj, resid = row_at_y(y_star, ident["N"], ident["Ny"])
            in_cand = jj in cands[lv]
            w = (w1_T_at(Tvals[lv], ident["N"], ident["Ny"], ident["dT"], ident["witness_gaps"], jj)
                 if in_cand else None)
            ok = bool(in_cand and w is not None and w <= STATION_FLOOR_T)
            per[lv] = dict(row=jj, y_over_b=y_over_b(jj, ident["N"]),
                           mapping_residual_b=resid, mapping_residual_cells=resid * ident["N"],
                           in_candidate_set=in_cand, W1_T=w, ok=ok,
                           identity_note=("IDENTITY on this level: the row was SELECTED by this "
                                          "criterion, so it cannot fail it. REPORTED, NOT "
                                          "EVIDENCE (VERIFICATION_CHARTER section 2a)."
                                          if lv == "f" else
                                          "CONTROL: the y/b came from the fine level and this "
                                          "level can fail it."))
            j_graded[lv] = jj
            print("      %s graded row %d at y/b = %.6f (mapping residual %.3e b = %.3f cells), "
                  "in candidate set %s, W1_T = %s / %.0e -> %s   [%s]"
                  % (CASES[lv], jj, per[lv]["y_over_b"], resid, per[lv]["mapping_residual_cells"],
                     in_cand, ("%.4e" % w) if w is not None else "n/a", STATION_FLOOR_T,
                     "ok" if ok else "FAIL", per[lv]["identity_note"]))
        station["per_level"] = per
        failed = [lv for lv in LEVELS if not per[lv]["ok"]]
        if failed:
            gate1_ok = False
            gate1_why.append("section 4 THREE-LEVEL CONSISTENCY: the selected y/b = %.6f does not "
                             "independently satisfy W1_T <= %.0e on %s. Selecting per level would "
                             "compare THREE DIFFERENT PHYSICAL LOCATIONS and the observed order "
                             "would be an artifact of the station drifting."
                             % (y_star, STATION_FLOOR_T, ",".join(CASES[lv] for lv in failed)))
            print("    THREE-LEVEL CONSISTENCY CLAUSE FAILS on %s -> the rung is NOT A RESULT "
                  "(section 4)." % ",".join(CASES[lv] for lv in failed))

    if not station.get("reachable"):
        return _write_unreachable(root, json_out, reg, idents, times, comp, reg_reads, ct,
                                  station, gate1_why, prov)

    # ---- (v) C_PROFILE AND THE REMAINING GATE-(1) CLAUSES -------------------
    print("(v) C_PROFILE at the SELECTED station, tolerance %.0e CARRIED OVER UNCHANGED from "
          "analyse_t16.py:573 (section 9: it is NOT relaxed, it is MOVED to where the referent is "
          "valid), and the remaining gate-(1) clauses:" % C_PROFILE_TOL)
    reads, prev, conv = {}, {}, {}
    for lv in LEVELS:
        ident = idents[lv]
        d = os.path.join(root, CASES[lv])
        r = readers(d, times[lv][-1], ident, j_row=j_graded[lv])
        r0 = readers(d, times[lv][-2], ident, j_row=j_graded[lv])
        reads[lv], prev[lv] = r, r0
        c = iterative_convergence(d, ident["endTime"])
        conv[lv] = c
        c["profile_slope_rel"] = r["T_slope_rel"]
        c["profile_monotone"] = r["T_monotone"]
        c["profile_ok"] = bool(r["T_monotone"] and abs(r["T_slope_rel"]) <= C_PROFILE_TOL)
        plat = abs(r["G1"] - r0["G1"]) / abs(r["G1"]) if r["G1"] != 0.0 else float("inf")
        c["plateau_rel_change"] = plat
        c["plateau_ok"] = plat <= PLAT_FLOOR
        c["W1_v"], c["W1_g"], c["W1_T"] = r["W1_v_max"], r["W1_g_max"], r["W1_T_max"]
        c["W1_ok"] = (r["W1_v_max"] <= W1_FLOOR_V and r["W1_g_max"] <= W1_FLOOR_G
                      and r["W1_T_max"] <= W1_FLOOR_T)
        c["mass_dev"] = r["mass_dev"]
        c["mass_ok"] = r["mass_dev"] <= MASS_FLOOR
        c["reversed_cells"] = r["reversed_cells"]
        c["v_min"] = r["v_min"]
        print("  %s gate (1) at row %d: C_PROFILE %s (monotone %s, slope/(-dT) - 1 = %+.3e / "
              "%.0e) | C_CONV %s (worst final-10%% initial residuals %s; Ux REPORTED %s) | "
              "C_PLAT %s (%.3e) | W1 %s (row-max v %.3e / %.0e, GRADED READER g %.3e / %.0e, "
              "T %.3e / %.0e) | C_MASS %s (%.3e) | C_REV %d reversed cell(s), min v/U0 %+.6f"
              % (CASES[lv], j_graded[lv], "ok" if c["profile_ok"] else "FAIL", r["T_monotone"],
                 r["T_slope_rel"], C_PROFILE_TOL,
                 "ok" if c["ok"] else "FAIL " + c["why"],
                 {k: ("%.2e" % v if v is not None else None) for k, v in c.get("worst", {}).items() if k != "Ux"},
                 ("%.2e" % c["Ux_reported_not_gated"]) if c.get("Ux_reported_not_gated") is not None else "n/a",
                 "ok" if c["plateau_ok"] else "FAIL", plat,
                 "ok" if c["W1_ok"] else "FAIL", r["W1_v_max"], W1_FLOOR_V, r["W1_g_max"],
                 W1_FLOOR_G, r["W1_T_max"], W1_FLOOR_T,
                 "ok" if c["mass_ok"] else "FAIL", r["mass_dev"], r["reversed_cells"], r["v_min"]))
        for name, ok in (("C_PROFILE", c["profile_ok"]), ("C_CONV", c["ok"]),
                         ("C_PLAT", c["plateau_ok"]), ("W1", c["W1_ok"]),
                         ("C_MASS", c["mass_ok"]), ("C_REV", c["reversed_cells"] == 0)):
            if not ok:
                gate1_ok = False
                gate1_why.append("%s fails %s" % (CASES[lv], name))

    # ---- planted-zero controls, rule 3 -------------------------------------
    control = planted_zero_controls(os.path.join(root, CASES["f"]), times["f"][-1], idents["f"],
                                    j_graded["f"])
    for k, v in control.items():
        print("planted-zero control %s PASS: %s plant %.4g in %s (%d cell(s)), recovered %.4g, "
              "demonstrated detection floor %g x scale"
              % (k, v["shape"], v["plant"], v["field"], v["cells_planted"], v["recovered"],
                 v["demonstrated_detection_floor"]))
    st_ctl = {}
    for lv in LEVELS:
        st_ctl[lv] = station_metric_planted_control(os.path.join(root, CASES[lv]), times[lv][-1],
                                                    idents[lv], j_graded[lv])
        c = st_ctl[lv]
        print("station-metric planted control %s PASS: plant %.4e (relative) into cell %d of "
              "witness row %d, base %.4e -> reader %.6e; acceptance %s; ULP at T_hot %.6e, the "
              "rejected 1e-15 slack is %.4g ULP and the chosen relative slack is %.4g ULP"
              % (CASES[lv], c["plant"], c["cell"], c["witness_row"], c["base"], c["got"],
                 c["acceptance"], c["ulp_at_T_hot"], c["t3_slack_in_ulp"], c["chosen_slack_in_ulp"]))

    # ---- (vi) ROACHE CLASSIFICATION, THEN THE BAND -------------------------
    print("(vi) Roache classification then the band (rule 5, Fs = %.2f):" % FS)
    rows = []
    G = reg["graded_rows"]
    specs = [
        ("G1", G["G1"]["quantity"], "G1", EX.U_STAR, G["G1"]["band_rel"], "rel", False),
        ("G1b", G["G1b"]["quantity"], "G1b", EX.Y_MAX, G["G1b"]["band_abs"], "abs", False),
        ("G3", G["G3"]["quantity"], "G3", EX.SHEAR_RATIO, G["G3"]["band_rel"], "rel", False),
        ("G2", G["G2"]["quantity"], "G2", 0.0, G["G2"]["floor_abs"], "abs", True),
    ]
    for rid, label, key, ref, width, kind, exact_class in specs:
        vals = {lv: reads[lv][key] for lv in LEVELS}
        tr = triple_of(vals)
        if kind == "rel":
            lo, hi = ref * (1 - width), ref * (1 + width)
        else:
            lo, hi = ref - width, ref + width
        verdict, bv, note = apply_gate(vals["f"], lo, hi, tr, gate1_ok, "; ".join(gate1_why), exact_class)
        dev = vals["f"] - ref
        rows.append(dict(row=rid, quantity=label, reference=ref, band=[lo, hi],
                         exact_class=exact_class, value_fine=vals["f"], triple=vals,
                         triple_state=tr["state"], triple_monotone=monotone(tr),
                         observed_order=tr.get("order"),
                         gci_pct=tr.get("GCI_pct"), richardson_REPORTED_ONLY=tr.get("richardson"),
                         deviation=dev, rel_deviation=(dev / ref) if ref else None,
                         graded_rows={lv: j_graded[lv] for lv in LEVELS},
                         band_verdict=bv, verdict=verdict, note=note,
                         extra=(dict(tau_hot=reads["f"]["tau_hot"], tau_cold=reads["f"]["tau_cold"])
                                if rid == "G3" else {})))
        print("%-3s fine=%.10e ref=%.10e dev=%+.3e%s band=[%.6e, %.6e] triple=(%.8e, %.8e, %.8e) %s "
              "-> %s%s"
              % (rid, vals["f"], ref, dev, (" (rel %+.3e)" % (dev / ref)) if ref else "", lo, hi,
                 vals["c"], vals["m"], vals["f"], fmt_tr(tr), verdict,
                 ("  [" + note + "]") if note else ""))
    if not gate1_ok:
        print("gate (1) FAILED: " + "; ".join(gate1_why))
    out = dict(rung="T16c", predecessor="T16", solver="buoyantBoussinesqSimpleFoam laminar",
               frozen_preregistration="docs/campaigns/T-family/T16c_PREREGISTRATION.md",
               frozen_preregistration_sha256=
               "0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f",
               pinned=dict(path=REG_PATH, sha256=REG_SHA256),
               provenance_reported_not_gated=prov,
               G_mix=EX.G_REG, G_reversal=EX.G_REVERSAL, dim=DIM,
               refinement_ratio=REFINEMENT, factor_of_safety=FS,
               floors=dict(STAGNANT_FLOOR=STAGNANT_FLOOR, P_MIN=P_MIN, CONV_FLOOR=CONV_FLOOR,
                           PLAT_FLOOR=PLAT_FLOOR, W1_FLOOR_V=W1_FLOOR_V, W1_FLOOR_G=W1_FLOOR_G,
                           W1_FLOOR_T=W1_FLOOR_T, MASS_FLOOR=MASS_FLOOR,
                           C_TRANSPOSE_TOL=C_TRANSPOSE_TOL, C_PROFILE_TOL=C_PROFILE_TOL,
                           STATION_FLOOR_T=STATION_FLOOR_T),
               identities={lv: idents[lv] for lv in LEVELS}, times=times,
               completion={lv: comp[lv] for lv in LEVELS},
               witnesses_at_registered_station={lv: reg_reads[lv] for lv in LEVELS},
               C_TRANSPOSE=ct, station=station,
               gate1=dict(ok=gate1_ok, why=gate1_why, per_level=conv),
               readers={lv: reads[lv] for lv in LEVELS}, planted_zero_controls=control,
               station_metric_planted_controls=st_ctl, rows=rows)
    json.dump(out, open(json_out, "w"), indent=2, default=str)
    print("wrote %s" % json_out)
    return EXIT_OK


def _write_unreachable(root, json_out, reg, idents, times, comp, reg_reads, ct, station,
                       gate1_why, prov):
    """SECTION 4's UNREACHABLE BRANCH.  Every graded row is NOT A RESULT and
    CARRIES NO VALUE: with no station there is no row to read, and a value
    invented for the record would be exactly the thing the branch exists to
    refuse.  The witnesses of step (ii) are written out in full, because they
    are the diagnosis."""
    rows = []
    for rid in ("G1", "G1b", "G3", "G2"):
        rows.append(dict(row=rid, quantity=reg["graded_rows"][rid]["quantity"],
                         value_fine=None, triple=None, triple_state=None,
                         verdict="NOT A RESULT", band_verdict=None,
                         note="gate (1): " + "; ".join(gate1_why)))
        print("%-3s value=NONE (no station was selected) -> NOT A RESULT" % rid)
    print("gate (1) FAILED: " + "; ".join(gate1_why))
    out = dict(rung="T16c", predecessor="T16",
               frozen_preregistration="docs/campaigns/T-family/T16c_PREREGISTRATION.md",
               frozen_preregistration_sha256=
               "0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f",
               pinned=dict(path=REG_PATH, sha256=REG_SHA256),
               provenance_reported_not_gated=prov,
               identities={lv: idents[lv] for lv in LEVELS}, times=times,
               completion={lv: comp[lv] for lv in LEVELS},
               witnesses_at_registered_station={lv: reg_reads[lv] for lv in LEVELS},
               C_TRANSPOSE=ct, station=station,
               gate1=dict(ok=False, why=gate1_why), rows=rows)
    json.dump(out, open(json_out, "w"), indent=2, default=str)
    print("wrote %s" % json_out)
    return EXIT_OK


# ==========================================================================
#                          S8 -- THE SELFTEST GUARDS
# ==========================================================================
def _selftest_root_guard(root, limb):
    """S8a.  REFUSES (exit 2) if a selftest arm's grading root is, contains or is
    contained by a LIVE run tree.

    THIS IS NOT HYPOTHETICAL.  `analyse_t18.py:509` reads `grade(HERE, ...)`
    with HERE the live T18_runs; it fired on 2026-08-31 and left
    T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.json, byte-identical
    (sha256 335bbec520a20ff4...) to the gate_t18.json written five minutes
    later.  A selftest that grades live data manufactures a verdict nobody
    registered.  This guard runs BEFORE ANY READ, so a refusal here leaves the
    live tree untouched -- which the S8c watcher then measures."""
    r = os.path.realpath(os.path.abspath(root))
    for live in LIVE_ROOTS:
        lr = os.path.realpath(live)
        if r == lr or r.startswith(lr + os.sep) or lr.startswith(r + os.sep):
            refuse("S8a -- the selftest limb %r was pointed at %s, which is, contains or is "
                   "inside the LIVE run tree %s. A selftest that grades a live tree manufactures "
                   "a verdict nobody registered (analyse_t18.py:509 did exactly this and its "
                   "side-effect file is byte-identical to the real gate). REFUSED before any "
                   "read." % (limb, r, lr))
    return True


def _selftest_grade(root, json_out, reg, limb="unnamed"):
    """The ONLY route by which the selftest may reach `grade`.  S8a then S8b,
    both before any read of `root`."""
    _selftest_root_guard(root, limb)
    sentinel = os.path.join(root, FORGE_SENTINEL)
    if not os.path.isfile(sentinel):
        refuse("S8b -- the selftest limb %r was pointed at %s, which carries no %s sentinel. "
               "S8a is a PATH test and a symlink defeats a path test; S8b is a POSITIVE marker "
               "that only this file's forge writes, so no real run tree can acquire one by "
               "accident. REFUSED." % (limb, root, FORGE_SENTINEL))
    return grade(root, json_out, reg)


class _RootWatch(object):
    """S8c -- RULE 3 APPLIED TO THE SELFTEST ITSELF.  Adapted from
    `T19b_runs/analyse_t19b.py:690`.

    Records every filesystem READ under `root` for the duration of the `with`
    block, by replacing the seven call routes through which this comparator can
    reach a run tree.  Paths in `allow` are permitted and not counted.

    A ZERO FROM THIS WATCHER IS NOT EVIDENCE UNTIL THE WATCHER HAS BEEN SHOWN
    ABLE TO SEE A NON-ZERO, so `selftest()` plants a deliberate read it must
    record, checks the record, and only then clears it."""

    def __init__(self, root, allow=()):
        self.root = os.path.abspath(root)
        self.allow = set(os.path.abspath(a) for a in allow)
        self.hits = []
        self._saved = None
        self._in = False

    def _note(self, p):
        if self._in:
            return
        self._in = True
        try:
            if isinstance(p, bytes):
                p = p.decode("utf-8", "replace")
            if not isinstance(p, str):
                p = os.fspath(p)
            ap = os.path.abspath(p)
            if (ap == self.root or ap.startswith(self.root + os.sep)) and ap not in self.allow:
                self.hits.append(ap)
        except Exception:
            pass
        finally:
            self._in = False

    def __enter__(self):
        import builtins
        import glob as _glob
        self._saved = (builtins.open, os.listdir, os.scandir, os.path.isfile,
                       os.path.isdir, os.path.exists, _glob.glob)
        w = self

        def wrap(fn):
            def g(path, *a, **k):
                if isinstance(path, (str, bytes)) or hasattr(path, "__fspath__"):
                    w._note(path)
                return fn(path, *a, **k)
            return g
        builtins.open = wrap(self._saved[0])
        os.listdir = wrap(self._saved[1])
        os.scandir = wrap(self._saved[2])
        os.path.isfile = wrap(self._saved[3])
        os.path.isdir = wrap(self._saved[4])
        os.path.exists = wrap(self._saved[5])
        _glob.glob = wrap(self._saved[6])
        return self

    def __exit__(self, *exc):
        import builtins
        import glob as _glob
        (builtins.open, os.listdir, os.scandir, os.path.isfile,
         os.path.isdir, os.path.exists, _glob.glob) = self._saved
        return False


def _unguarded_grade_calls_in_selftest(src=None):
    """S8d -- the SOURCE-LEVEL detector, aimed at the ACTUAL defect shape.

    `analyse_t18.py:509` reads `grade(HERE, ...)`: a call to the BARE grading
    function from inside a selftest, with a live root as its first argument.
    The invariant this file holds is stronger and easier to check than "no live
    name appears anywhere" -- that formulation would flag L32, which references
    the live root ON PURPOSE in order to DRIVE the refusal:

        NO SELFTEST FUNCTION CALLS `grade(...)` DIRECTLY.  Every route to the
        grader goes through `_selftest_grade`, which carries S8a and S8b.

    So the detector counts direct `grade(...)` calls inside the selftest and
    forge bodies.  It must be 0, and `selftest()` drives this SAME function on a
    PLANTED `grade(HERE, ...)` source to show it returns a non-zero -- a zero
    from a detector never shown able to see a non-zero is not evidence."""
    import ast as _a
    # `_selftest_grade` is DELIBERATELY absent: it is the ONE sanctioned call
    # site, and it calls `grade` only after S8a and S8b have both passed.
    fns = {"selftest", "_forge_case", "_run_forged"}
    tree = _a.parse(src if src is not None else open(os.path.abspath(__file__)).read())
    n = 0
    for node in _a.walk(tree):
        if isinstance(node, _a.FunctionDef) and node.name in fns:
            for sub in _a.walk(node):
                if (isinstance(sub, _a.Call) and isinstance(sub.func, _a.Name)
                        and sub.func.id == "grade"):
                    n += 1
    return n


# ---------------------------------------------------------------- the forge
def _forge_case(root, lv, N, transpose=False, witness_bump=0.0, uniform_T=False,
                residual=1e-9, plateau_bump=0.0, g_mutant=False, mass_bump=0.0,
                reversal=False, entry_amp=0.0, entry_dev_b=20.0, never_develops=False,
                bump_about_b=None):
    """A synthetic finished case shaped like a T16 run.  ADAPTED from
    `analyse_t16.py:660-736`, with THREE additions, all of them for limbs T16
    could not have, and every forged tree carries the S8b sentinel.

    THE DEVELOPMENT LAW, and why it is a RAMP TO EXACTLY ZERO rather than an
    exponential.  The forged temperature is

        T(j, i) = T_lin(i) + entry_amp * dT * ramp(y_j) * sin(pi Y_i),
        ramp(y)  = max(0, 1 - y / entry_dev_b)          (the developing forge)
        ramp(y)  =         1 - y / entry_dev_b          (`never_develops`)

    with `y_j = (j + 0.5)/N` the PHYSICAL streamwise coordinate in units of b,
    so the law is IDENTICAL on all three levels and nothing about it is
    level-indexed.

    A SMOOTH decay was tried first and REJECTED, and the reason is a real
    property of the frozen rule rather than a convenience: under any smooth
    decay the "smallest j" selection lands the station EXACTLY AT THE FLOOR
    CROSSING, where W1_T sits within one refinement step of 1e-06.  The
    three-level consistency clause then turns on a mapping residual of up to
    half a coarse cell, and the limb would be measuring the forge's steepness
    rather than the rule.  With a ramp to exactly zero, W1_T is EXACTLY 0 for
    every row all of whose registered witness offsets lie beyond
    `entry_dev_b`, and is >= entry_amp/(offset span) below it, so the crossing
    is unambiguous on every level and the limb tests the rule.

    THAT FRAGILITY IS NOT A FORGE ARTEFACT AND IT IS REPORTED, NOT HIDDEN: on a
    real solve the station WILL sit at the floor crossing, and how much margin
    the coarse and medium levels then have at the same y/b is not something
    this comparator can promise.  The comparator PRINTS each level's W1_T and
    its mapping residual for exactly that reason.

    `bump_about_b` IS THE THIRD ADDITION AND IT EXISTS BECAUSE THE STATION
    MOVED.  `analyse_t16.py`'s forge indexes its witness and mass perturbations
    off `build_t16.STATION_B` -- T16's REGISTERED station at 48b.  T16c grades
    at the station section 4 SELECTS, so a perturbation placed at 48b lands 40b
    away from the graded row and the W1 and C_MASS limbs go green while testing
    nothing.  That is not a cosmetic difference: it is the first thing the
    frozen document's repair breaks in the inherited test harness, and it was
    MEASURED here as two red limbs rather than reasoned about.  The limbs now
    place the perturbation at the row the candidate-set formula makes the
    smallest candidate -- 8b, derived from the formula and NOT from running the
    comparator.

    Rule 4 is satisfied by construction -- rc = 0 in STATUS, an End line,
    endTime ExecutionTime lines, the registered fields, and `0/T` stamped OLDER
    than every written field so the age guard passes on an honest forge."""
    case = os.path.join(root, CASES[lv])
    Ny = B.ASPECT * N
    os.makedirs(os.path.join(case, "system"))
    os.makedirs(os.path.join(case, "constant"))
    os.makedirs(os.path.join(case, "0.orig"))
    os.makedirs(os.path.join(case, "0"))
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(B.block_mesh_dict(N, B.ASPECT))
    et = B.END_TIME[lv]
    open(os.path.join(case, "system", "controlDict"), "w").write(B.control_dict(et))
    for k, v in B.constant_files().items():
        if g_mutant and k == "transportProperties":
            v = v.replace("nu              %.17g" % B.NU, "nu              %.17g" % (B.NU * 1.01))
        open(os.path.join(case, "constant", k), "w").write(v)
    for k, v in B.fields().items():
        open(os.path.join(case, "0.orig", k), "w").write(v)
        open(os.path.join(case, "0", k), "w").write(v)
    Y, ph = EX.discrete_profile(N)
    j0 = int(round((B.STATION_B if bump_about_b is None else bump_about_b) * N))
    j_wit = j0 + B.WITNESS_B[0] * N

    def t_entry(j, i):
        """The DEVELOPING temperature described in this function's docstring.  It
        is a forge, not a solution; what matters is that W1_T(j) is LARGE near
        the inlet and EXACTLY ZERO past a station this test computes
        independently of the comparator."""
        lin = B.T_HOT - B.DT * Y[i]
        if entry_amp == 0.0:
            return lin
        r = 1.0 - ((j + 0.5) / N) / entry_dev_b
        if not never_develops:
            r = max(0.0, r)
        return lin + entry_amp * B.DT * r * math.sin(math.pi * Y[i])

    def write_time(t, bump):
        td = os.path.join(case, str(t))
        os.makedirs(td)
        Uv, Tv = [], []
        for j in range(Ny):
            for i in range(N):
                ii, jj = (j % N, i) if transpose else (i, j)   # transpose: y-fastest ordering
                v = B.U0 * ph[ii] * (1.0 + bump)
                if witness_bump and jj == j_wit:
                    v *= (1.0 + witness_bump)
                if mass_bump and jj == j0:
                    v *= (1.0 + mass_bump)
                if reversal and ii == 0:
                    v = -1.0e-9 * B.U0
                Uv.append("(0 %.17g 0)" % v)
                Tv.append("%.17g" % t_entry(jj, ii))

        def hdr(cls, obj):
            return B.head(cls, obj, str(t))
        open(os.path.join(td, "U"), "w").write(
            hdr("volVectorField", "U") + "dimensions [0 1 -1 0 0 0 0];\ninternalField nonuniform "
            "List<vector> \n%d\n(\n%s\n)\n;\nboundaryField { }\n" % (N * Ny, "\n".join(Uv)))
        if uniform_T:
            open(os.path.join(td, "T"), "w").write(
                hdr("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\ninternalField uniform 300;\n"
                "boundaryField { }\n")
        else:
            open(os.path.join(td, "T"), "w").write(
                hdr("volScalarField", "T") + "dimensions [0 0 0 1 0 0 0];\ninternalField nonuniform "
                "List<scalar> \n%d\n(\n%s\n)\n;\nboundaryField { }\n" % (N * Ny, "\n".join(Tv)))
        for f in ("p_rgh", "phi"):
            open(os.path.join(td, f), "w").write(hdr("volScalarField", f) + "internalField uniform 0;\n")
    write_time(et - et // 10, plateau_bump)
    write_time(et, 0.0)
    with open(os.path.join(case, "log.solve"), "w") as fh:
        for it in range(1, et + 1):
            r = residual if it > 0.9 * et else 1e-3
            fh.write("Time = %d\n" % it)
            for f in ("Ux", "Uy", "T", "p_rgh"):
                fh.write("solver:  Solving for %s, Initial residual = %.3e, Final residual = 1e-12, "
                         "No Iterations 1\n" % (f, 0.05 if f == "Ux" else r))
            fh.write("ExecutionTime = 1 s  ClockTime = 1 s\n\n")
        fh.write("End\n")
    open(os.path.join(root, "STATUS.%s" % CASES[lv]), "w").write("case=%s\nrc=0\ncapped=no\n" % CASES[lv])
    open(os.path.join(root, "DONE.%s" % CASES[lv]), "w").write("forged\n")
    open(os.path.join(root, FORGE_SENTINEL), "w").write(
        "This tree was FORGED by analyse_t16c.py --selftest. It is NOT a run and nothing in it "
        "is a result. S8b refuses to grade any tree without this file.\n")
    # RULE 4's AGE GUARD, honoured by the forge rather than accidentally
    # satisfied: `0/T` is touched LAST AT LAUNCH, so on a completed run it is
    # OLDER than every field the run wrote.  Stamping it an hour back makes the
    # forge an honest completed run instead of one that passes because two
    # writes landed in the same second.
    _old = os.path.getmtime(os.path.join(case, str(et), "T")) - 3600.0
    os.utime(os.path.join(case, "0", "T"), (_old, _old))


def _strip_end_line(p):
    """L30's control: remove the `End` line from log.solve and NOTHING ELSE.

    THE DEFECT THIS REPLACES, recorded because the limb looked green while
    testing the wrong conjunct.  The control was

        open(p, "w").write(open(p).read().replace("End\\n", ""))

    and `open(p, "w")` TRUNCATES the file at the moment it is evaluated, which
    Python does BEFORE it evaluates the argument expression `open(p).read()`.
    The read therefore returns the empty string and the control EMPTIES
    log.solve rather than removing one line.  An emptied log has no
    `ExecutionTime` lines either, so the refusal it produces comes from the
    count conjunct at :515 and the `End`-line conjunct at :511 that L30 names
    is never exercised.  MEASURED consequence: mutation M31, which disables
    :511 exactly, left L30 GREEN -- the limb had no control that reddened it.

    This form reads first, writes second, and then READS THE FILE BACK and
    refuses unless the edit removed the End line and left the ExecutionTime
    lines standing.  A control that is not shown to have planted what it
    claims is not a control.
    """
    txt = open(p).read()
    if not re.search(r"^End\s*$", txt, re.M):
        refuse("L30 control: log.solve at %s carries no End line to remove -- a control "
               "cannot plant what is not there" % p)
    n_et = len(re.findall(r"^ExecutionTime = ", txt, re.M))
    with open(p, "w") as fh:
        fh.write(txt.replace("End\n", ""))
    back = open(p).read()
    if re.search(r"^End\s*$", back, re.M):
        refuse("L30 control: the End line SURVIVED the edit in %s" % p)
    if len(re.findall(r"^ExecutionTime = ", back, re.M)) != n_et:
        refuse("L30 control: the edit changed the ExecutionTime count in %s from %d to %d -- "
               "the control must remove ONE conjunct's evidence, not empty the file, or the "
               "limb re-tests the count conjunct at :515 instead of the End line at :511"
               % (p, n_et, len(re.findall(r"^ExecutionTime = ", back, re.M))))
    return len(back)


def selftest():
    import ast
    import subprocess
    fails = []
    reg = load_registered()
    _station_floor_identity_check()
    print("analyse_t16c selftest.  Every limb runs against a SYNTHETIC forged tree in a scratch "
          "directory; S8 watchers measure that no limb touched a live one.")
    print("  frozen authority: docs/campaigns/T-family/T16c_PREREGISTRATION.md "
          "sha256 0b425c40974581484f9ce91c44ad7bb3d4956fb1e81dad0ce03e7ba7e01bcd3f")

    def ok_(label, cond, limb):
        print("  [%s] %-4s %s" % ("ok " if cond else "FAIL", limb, label))
        if not cond:
            fails.append(limb)
        return cond

    FORGE_N = {"c": 5, "m": 10, "f": 20}
    # The forge's ASPECT is 64, so Ny = 64 N and the registered witness offsets
    # (+-4b, +-8b) put the candidate set at rows [8N, 56N), i.e. y/b in [8, 56).
    # ENTRY_DEV_B = 20 puts the development front comfortably inside it: the
    # first row all of whose witness offsets clear the front is the smallest j
    # with y_(j-8N) >= 20, and that is the SAME PHYSICAL STATION on every level.
    ENTRY_AMP, ENTRY_DEV_B = 1.0e-2, 20.0

    def entry_kw(_N=None):
        # A PHYSICAL law in y/b, identical on every level.  Nothing is indexed
        # by N, so the three levels develop at the same place by construction
        # and the three-level consistency limb measures the RULE rather than a
        # level-dependent artefact of the forge.
        return dict(entry_amp=ENTRY_AMP, entry_dev_b=ENTRY_DEV_B)

    # ---------------- S8: the watchers, armed for the WHOLE selftest ----------
    watch_parent = _RootWatch(PARENT, allow=(REG_PATH, EXACT_PATH, BUILD_PATH, T16_PATH,
                                             os.path.join(PARENT, "__pycache__")))
    watch_here = _RootWatch(HERE, allow=(os.path.abspath(__file__),))
    with watch_parent, watch_here:
        # S8c PLANTED CONTROL: a zero from these watchers is not evidence until
        # each has been shown able to see a non-zero.
        os.path.isfile(os.path.join(PARENT, "run_one_t16.sh"))
        os.path.isfile(os.path.join(HERE, FORGE_SENTINEL))
        planted_parent = len(watch_parent.hits)
        planted_here = len(watch_here.hits)
        watch_parent.hits, watch_here.hits = [], []

        # ---------------- L01 the referent still verifies --------------------
        r, f = EX.verify(quiet=True)
        ok_("the referent's Route B verifies (B1 B2 B3 B4 B4b) -- the referent is NOT replaced "
            "(frozen document section 4.1)", (r is not None and not f), "L01")
        EX.selfcheck_readers()

        # ---------------- L02 the carried-over floors ARE the registered ones -
        fired = False
        tmpj = tempfile.mkdtemp(prefix="t16creg_")
        try:
            bad = dict(reg)
            bad["roache_floors"] = dict(reg["roache_floors"], P_MIN=0.5)
            json.dump(bad, open(os.path.join(tmpj, "T16_registered.json"), "w"))
            try:
                load_registered(here=tmpj)
            except SystemExit as e:
                fired = (e.code == EXIT_REFUSE)
        finally:
            shutil.rmtree(tmpj, ignore_errors=True)
        ok_("registered P_MIN mutated to 0.5 -> REFUSE (import %g / %g is the one number)"
            % (STAGNANT_FLOOR, P_MIN), fired, "L02")

        # ---------------- L03 a carried-over floor that MOVED is refused ------
        fired = False
        tmpj = tempfile.mkdtemp(prefix="t16creg2_")
        try:
            bad = json.loads(json.dumps(reg))
            bad["controls"]["W1"]["floor_T"] = 1e-5
            json.dump(bad, open(os.path.join(tmpj, "T16_registered.json"), "w"))
            try:
                load_registered(here=tmpj)
            except SystemExit as e:
                fired = (e.code == EXIT_REFUSE)
        finally:
            shutil.rmtree(tmpj, ignore_errors=True)
        ok_("registered W1 floor_T RELAXED to 1e-5 -> REFUSE (frozen document section 9: the "
            "1e-06 tolerance is NOT relaxed, and a registration that relaxes it stops the run)",
            fired, "L03")

        # ---------------- L04 the section 5 PIN -------------------------------
        fired = False
        tmpj = tempfile.mkdtemp(prefix="t16cpin_")
        try:
            shutil.copy2(REG_PATH, os.path.join(tmpj, "T16_registered.json"))
            with open(os.path.join(tmpj, "T16_registered.json"), "a") as fh:
                fh.write("\n")
            try:
                pin(os.path.join(tmpj, "T16_registered.json"), REG_SHA256, "T16_registered.json")
            except SystemExit as e:
                fired = (e.code == EXIT_REFUSE)
        finally:
            shutil.rmtree(tmpj, ignore_errors=True)
        ok_("one byte appended to a copy of the pinned registration -> REFUSE (frozen document "
            "section 5: a moved gate fails CLOSED instead of grading quietly)", fired, "L04")
        ok_("the live pinned registration reproduces its registered digest %s..." % REG_SHA256[:16],
            sha256_of(REG_PATH) == REG_SHA256, "L05")

        # ---------------- L06 rule 5 through apply_gate ------------------------
        ref = EX.U_STAR
        width = reg["graded_rows"]["G1"]["band_rel"]
        lo, hi = ref * (1 - width), ref * (1 + width)

        def ladder(p, e_f=None):
            e_f = (0.4 * width * ref) if e_f is None else e_f
            return dict(f=ref + e_f, m=ref + e_f * 2 ** p, c=ref + e_f * 4 ** p)

        rule5_ok = True
        for label, vals, want, want_gci in (
                ("healthy p=2.000", ladder(2.0), "PASS", True),
                ("p=0.51 (just above STAGNANT_FLOOR)", ladder(0.51), "PASS", True),
                ("p=0.49 -> STAGNANT", ladder(0.49), "NOT A RESULT", False),
                ("p=0.01 -> DEGENERATE", ladder(0.01), "NOT A RESULT", False),
                ("oscillatory", dict(c=ref + 1e-4, m=ref - 1e-4, f=ref + 5e-5), "NOT A RESULT", False),
                ("divergent", ladder(-1.0), "NOT A RESULT", False),
                ("healthy p=2 but fine OUTSIDE the band", ladder(2.0, e_f=3.0 * width * ref),
                 "GATE FAIL", True),
                ("gate (1) failed -> NOT A RESULT whatever the triple", ladder(2.0),
                 "NOT A RESULT", True)):
            tr = triple_of(vals)
            g1ok = "gate (1)" not in label
            v, bv, note = apply_gate(vals["f"], lo, hi, tr, g1ok, "forced", False)
            has_gci = tr.get("GCI_pct") is not None
            good = (v == want) and (has_gci == want_gci)
            rule5_ok = rule5_ok and good
            print("      %-50s %s -> %s" % (label, fmt_tr(tr), v))
        ok_("rule 5 order: not-converged/not-plateaued -> NOT A RESULT; "
            "DIVERGENT/STAGNANT/OSCILLATORY/EXACT -> NOT A RESULT with the triple printed; "
            "CONVERGING -> band; the gate is ONE-WAY", rule5_ok, "L06")

        # ---------------- L07 NEVER quote a GCI on a non-monotone triple -------
        mono_ok = True
        for vals in (dict(c=ref + 1e-4, m=ref - 1e-4, f=ref + 5e-5),
                     dict(c=ref - 1e-4, m=ref + 1e-4, f=ref - 5e-5),
                     dict(c=ref + 1e-4, m=ref + 3e-4, f=ref + 1e-4)):
            tr = triple_of(vals)
            if monotone(tr) is False and tr.get("GCI_pct") is not None:
                mono_ok = False
        ok_("rule 5: no GCI is quoted on any non-monotone triple (three shapes driven)",
            mono_ok, "L07")

        # ---------------- L08 EXACT-class rows --------------------------------
        tr = triple_of(dict(c=0.0, m=0.0, f=0.0))
        v, bv, note = apply_gate(0.0, -1e-6, 1e-6, tr, True, "", True)
        v2, _, _ = apply_gate(3e-6, -1e-6, 1e-6, tr, True, "", True)
        ok_("EXACT-class row: an EXACT triple is graded by its FLOOR (%s) and outside it is %s"
            % (v, v2), (tr["state"] == "EXACT" and v == "PASS" and v2 == "GATE FAIL"), "L08")

        # ---------------- the forge harness -----------------------------------
        def _run_forged(limb, **kw):
            tmp = tempfile.mkdtemp(prefix="t16cforge_")
            try:
                for lv in LEVELS:
                    k = dict(kw)
                    if k.pop("_entry", False):
                        k.update(entry_kw())
                    if k.pop("_drift", False):
                        # the FINE level develops at y/b = 20; the coarse and
                        # medium ones do not develop until y/b = 50, which is
                        # PAST the candidate set. The rule still selects a fine
                        # station, and the three-level consistency clause is
                        # then the only thing standing between that station and
                        # a triple built at three different physical places.
                        k.update(entry_kw())
                        if lv != "f":
                            k["entry_dev_b"] = 50.0
                    _forge_case(tmp, lv, FORGE_N[lv], **k)
                out = os.path.join(tmp, "gate.json")
                code = None
                try:
                    code = _selftest_grade(tmp, out, reg, limb=limb)
                except SystemExit as e:
                    code = e.code
                res = json.load(open(out)) if os.path.isfile(out) else None
                return code, res
            finally:
                shutil.rmtree(tmp, ignore_errors=True)

        # ---------------- L09 THE VALUE CONTROL, fully developed --------------
        code, res = _run_forged("value-control")
        exp = EX.discrete_expectation(FORGE_N["f"])
        rows = {r["row"]: r for r in res["rows"]} if res else {}
        _g1 = reg["graded_rows"]["G1"]["band_rel"]
        want_g1 = "PASS" if abs(exp["G1_rel_err"]) <= _g1 else "GATE FAIL"
        good = (code == 0 and rows
                and rows["G1"]["verdict"] == want_g1
                and abs(rows["G1"]["value_fine"] - exp["G1"]) < 1e-12
                and abs(rows["G1"]["observed_order"] - 2.0) < 0.15
                and rows["G2"]["verdict"] == "PASS"
                and abs(rows["G2"]["value_fine"]) < 1e-9
                and all(res["planted_zero_controls"][k]["status"] == "PASS"
                        for k in ("G1", "G1b", "G2", "G3", "W1_max"))
                and all(res["station_metric_planted_controls"][lv]["status"] == "PASS"
                        for lv in LEVELS))
        print("      forged ladder N = %d/%d/%d, FULLY DEVELOPED: station = first candidate row "
              "%s; G1 %s p=%s fine == the 1-D model to 1e-12; 5 + 3 planted controls"
              % (FORGE_N["c"], FORGE_N["m"], FORGE_N["f"],
                 res["station"]["fine_row"] if res else "?", want_g1,
                 ("%.4f" % rows["G1"]["observed_order"]) if rows else "?"))
        ok_("VALUE CONTROL: a forged ladder from the 1-D discrete model grades as the band "
            "ARITHMETIC at that N requires, and every planted control PASSES", good, "L09")

        # ---------------- L10 THE STATION RULE SELECTS A REAL STATION ---------
        code, res = _run_forged("station-selection", _entry=True)
        st = res["station"] if res else {}
        # THE ROW THE RULE MUST PICK, derived here from the FORGE'S OWN
        # DEFINITION and not from anything the comparator computed: W1_T(j) is
        # zero exactly when every registered witness offset clears the front,
        # i.e. when the FURTHEST UPSTREAM offset row -8b has y >= ENTRY_DEV_B.
        Nf = FORGE_N["f"]
        want_j = None
        for j in range(8 * Nf, 56 * Nf):
            if ((j - 8 * Nf) + 0.5) / Nf >= ENTRY_DEV_B:
                want_j = j
                break
        good = (code == 0 and st.get("reachable") and st.get("fine_row") == want_j
                and st["per_level"]["f"]["ok"] and st["per_level"]["c"]["ok"]
                and st["per_level"]["m"]["ok"])
        print("      developing forge (amp %.0e, front at y/b = %.1f): the rule selected fine "
              "row %s at y/b %s; an INDEPENDENT derivation from the forge's own definition says "
              "row %s; c/m mapped by y/b to rows %s/%s with mapping residuals %.3f/%.3f cells "
              "and W1_T %s/%s"
              % (ENTRY_AMP, ENTRY_DEV_B, st.get("fine_row"),
                 ("%.4f" % st["y_over_b"]) if st.get("y_over_b") else "?", want_j,
                 st.get("per_level", {}).get("c", {}).get("row"),
                 st.get("per_level", {}).get("m", {}).get("row"),
                 st.get("per_level", {}).get("c", {}).get("mapping_residual_cells", float("nan")),
                 st.get("per_level", {}).get("m", {}).get("mapping_residual_cells", float("nan")),
                 st.get("per_level", {}).get("c", {}).get("W1_T"),
                 st.get("per_level", {}).get("m", {}).get("W1_T")))
        ok_("STATION RULE (section 4): the SMALLEST candidate j on the FINE level reaching "
            "W1_T <= %.0e is the one an independent closed-form scan of the same forge names, "
            "and the three-level consistency clause passes" % STATION_FLOOR_T, good, "L10")

        # ---------------- L11 THE UNREACHABLE BRANCH --------------------------
        code, res = _run_forged("unreachable", entry_amp=ENTRY_AMP, entry_dev_b=ENTRY_DEV_B,
                                never_develops=True)
        good = (code == 0 and res and res["station"]["reachable"] is False
                and all(r["verdict"] == "NOT A RESULT" for r in res["rows"])
                and all(r["value_fine"] is None for r in res["rows"]))
        ok_("UNREACHABLE BRANCH (section 4): a forge whose entry perturbation NEVER decays -> "
            "NOT A RESULT on every row, NO VALUE recorded, the station NOT relocated, the "
            "threshold NOT loosened, the candidate set NOT widened", good, "L11")

        # ---------------- L12 THE THREE-LEVEL CONSISTENCY CLAUSE --------------
        code, res = _run_forged("three-level", _drift=True)
        good = (code == 0 and res and res["station"].get("reachable")
                and not res["gate1"]["ok"]
                and any("THREE-LEVEL CONSISTENCY" in w for w in res["gate1"]["why"])
                and all(r["verdict"] == "NOT A RESULT" for r in res["rows"]))
        ok_("THREE-LEVEL CONSISTENCY (section 4): a forge that develops on the FINE level but "
            "not at the same y/b on c and m -> NOT A RESULT. Selecting per level would compare "
            "THREE DIFFERENT PHYSICAL LOCATIONS.", good, "L12")

        # ---------------- L13 C_TRANSPOSE, the section 2 PLANTED control ------
        # Clause 2 of section 2: the SIGNATURE IS MEASURED, not asserted.
        tmp = tempfile.mkdtemp(prefix="t16ctr_")
        sig = None
        try:
            _forge_case(tmp, "c", FORGE_N["c"], transpose=True)
            d = os.path.join(tmp, CASES["c"])
            ident = case_identity(d, reg)
            t = latest_times(d, 1)[-1]
            sig = readers(d, t, ident)["T_slope_rel"]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        code, res = _run_forged("c-transpose", transpose=True)
        good = (code == EXIT_REFUSE and sig is not None
                and abs(sig - TRANSPOSE_SIGNATURE) <= TRANSPOSE_SIG_TOL)
        print("      a PLANTED transposed ordering, read through the REAL reader, returns "
              "slope/(-dT) - 1 = %.6f; the frozen document section 2 clause 2 requires it within "
              "%.1f of %.1f -- MEASURED, not asserted, which analyse_t16.py:922 never did"
              % (sig if sig is not None else float("nan"), TRANSPOSE_SIG_TOL, TRANSPOSE_SIGNATURE))
        ok_("C_TRANSPOSE POSITIVE ARM (section 2): a planted transpose REFUSES (exit %s) AND its "
            "signature is RECOVERED within %.1f of %.1f" % (code, TRANSPOSE_SIG_TOL,
                                                            TRANSPOSE_SIGNATURE), good, "L13")

        # ---------------- L14 C_TRANSPOSE NEGATIVE ARM ------------------------
        tmp = tempfile.mkdtemp(prefix="t16cntr_")
        neg = None
        try:
            _forge_case(tmp, "c", FORGE_N["c"], **entry_kw())
            d = os.path.join(tmp, CASES["c"])
            ident = case_identity(d, reg)
            t = latest_times(d, 1)[-1]
            neg = readers(d, t, ident)["T_slope_rel"]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        good = (neg is not None and abs(neg) < C_TRANSPOSE_TOL)
        print("      the UNTRANSPOSED forge returns slope/(-dT) - 1 = %+.6e, which is %.4g x "
              "inside the 0.5 threshold and does NOT fire the guard"
              % (neg, C_TRANSPOSE_TOL / abs(neg) if neg else float("inf")))
        ok_("C_TRANSPOSE NEGATIVE ARM (section 2, 'both arms or the guard is not admitted'): the "
            "untransposed case returns |slope/(-dT) - 1| < %.1f and does NOT fire"
            % C_TRANSPOSE_TOL, good, "L14")

        # ---------------- L15 THE D576 REPAIR, MEASURED -----------------------
        # The witness must be REACHED on a run that then REFUSES at C_TRANSPOSE.
        # This is the whole of frozen document section 3 and it is the one limb
        # that would have changed T16's outcome.
        tmp = tempfile.mkdtemp(prefix="t16cd576_")
        try:
            for lv in LEVELS:
                _forge_case(tmp, lv, FORGE_N[lv], transpose=True)
            out = os.path.join(tmp, "gate.json")
            import io
            import contextlib
            buf = io.StringIO()
            code = None
            with contextlib.redirect_stdout(buf):
                try:
                    code = _selftest_grade(tmp, out, reg, limb="d576")
                except SystemExit as e:
                    code = e.code
            txt = buf.getvalue()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        i_wit = txt.find("(ii) W1 DEVELOPMENT WITNESSES")
        i_ref = txt.find("REFUSE: C_TRANSPOSE")
        n_wit = txt.count("W1_v ")
        good = (code == EXIT_REFUSE and i_wit >= 0 and i_ref > i_wit and n_wit == 3)
        print("      on a REFUSING run the witness block appears at character %d and the refusal "
              "at character %d, and W1_v/W1_g/W1_T are printed for %d of 3 levels"
              % (i_wit, i_ref, n_wit))
        ok_("D576 REPAIR (section 3): W1_v, W1_g and W1_T are READ AND PRINTED for ALL THREE "
            "LEVELS BEFORE the guard refuses. In analyse_t16.py the refusal is at :573 and W1_T "
            "is first computed at :582 -- NINE LINES BELOW -- so the witness that carried the "
            "entire diagnosis was unreachable exactly when it was needed.", good, "L15")

        # ---------------- L16-L20 gate (1) arms, one at a time -----------------
        for limb, label, kw in (
                ("L16", "W1 development witness bumped 1e-4 on a witness row of the GRADED "
                        "station -> gate (1)", dict(witness_bump=1e-4, bump_about_b=8)),
                ("L17", "final-10% residual 1e-3, above the registered 1e-6 floor -> gate (1)",
                 dict(residual=1e-3)),
                ("L18", "G1 moved 1e-5 between the last two writes -> C_PLAT gate (1)",
                 dict(plateau_bump=1e-5)),
                ("L19", "GRADED station row mean scaled 1e-4 off U0 -> C_MASS gate (1)",
                 dict(mass_bump=1e-4, bump_about_b=8)),
                ("L20", "one REVERSED cell on the station row -> C_REV gate (1)",
                 dict(reversal=True))):
            code, res = _run_forged(limb, **kw)
            good = (code == 0 and res and all(r["verdict"] == "NOT A RESULT" for r in res["rows"])
                    and not res["gate1"]["ok"])
            ok_(label + " -> NOT A RESULT x4", good, limb)

        # ---------------- L21 uniform T, L22 the G mutant ----------------------
        for limb, label, kw in (
                ("L21", "uniform T at endTime -> REFUSE (a uniform field also produces the -1.0 "
                        "signature; read_field refuses it first)", dict(uniform_T=True)),
                ("L22", "nu mutated 1 percent in transportProperties -> C_G REFUSE",
                 dict(g_mutant=True))):
            code, res = _run_forged(limb, **kw)
            ok_(label + " (exit %s)" % code, code == EXIT_REFUSE, limb)

        # ---------------- L23 the planted-zero controls, both arms -------------
        tmp = tempfile.mkdtemp(prefix="t16cblind_")
        try:
            _forge_case(tmp, "c", FORGE_N["c"], **entry_kw())
            d = os.path.join(tmp, CASES["c"])
            ident = case_identity(d, reg)
            t = latest_times(d, 1)[-1]
            good_read = readers(d, t, ident)

            def blind(case_dir, time, ident, j_row=None):
                return dict(good_read)          # the same numbers whatever is on disk

            fired = False
            try:
                planted_zero_controls(d, t, ident, ident["j_station"], read=blind)
            except SystemExit as e:
                fired = (e.code == EXIT_REFUSE)
            ok_("BLIND reader mutant (ignores the plant) -> planted-zero control REFUSES",
                fired, "L23")

            rep = planted_zero_controls(d, t, ident, ident["j_station"])
            good = (all(rep[k]["status"] == "PASS" for k in rep)
                    and rep["G2"]["cells_planted"] == FORGE_N["c"]
                    and rep["G2"]["shape"] == "ALL-ROW ALTERNATING SIGN")
            ok_("real reader: 5/5 carried-over planted controls PASS; G2's plant covers all %d "
                "row cells and ALTERNATES IN SIGN (L-340)" % rep["G2"]["cells_planted"],
                good, "L24")

            # ------------ L25 the NEW station reader's planted control ---------
            ctl = station_metric_planted_control(d, t, ident, ident["j_station"])
            print("      base %.6e, plant %.6e, reader returned %.6e; acceptance %s"
                  % (ctl["base"], ctl["plant"], ctl["got"], ctl["acceptance"]))
            print("      PREDICATE PROVENANCE: %s. REJECTED: %s. One ULP at T_hot = %.6e K, so "
                  "the rejected 1e-15 slack is %.4g ULP (BELOW one ULP, decided by a residual "
                  "wiggle) and the chosen relative slack is %.4g ULP."
                  % (ctl["predicate_source"], ctl["rejected_predicate"], ctl["ulp_at_T_hot"],
                     ctl["t3_slack_in_ulp"], ctl["chosen_slack_in_ulp"]))
            good = (ctl["status"] == "PASS" and ctl["t3_slack_in_ulp"] < 1.0
                    and ctl["chosen_slack_in_ulp"] > 1.0)
            ok_("STATION READER planted control (rule 3): the plant is RECOVERED under the "
                "family's RELATIVE predicate, and the rejected T3 predicate's slack is MEASURED "
                "below one ULP while the chosen one is above it", good, "L25")

            # ------------ L26 a BLIND station reader is refused ----------------
            def blind_T(case_dir, time):
                return list(read_field(d, t, "T"))      # always the unplanted original

            fired = False
            try:
                station_metric_planted_control(d, t, ident, ident["j_station"], read_T=blind_T)
            except SystemExit as e:
                fired = (e.code == EXIT_REFUSE)
            ok_("BLIND station reader (returns the unplanted field whatever is on disk) -> the "
                "station-metric control REFUSES. Without this limb a station selected at the "
                "FIRST candidate row would be indistinguishable from one selected on evidence.",
                fired, "L26")

            # ------------ L27 the fast scanner IS the frozen reader ------------
            cand = candidate_rows(ident["N"], ident["Ny"], ident["witness_gaps"])
            Tv = read_field(d, t, "T")
            agreed = station_metric_agreement(d, t, ident, Tv,
                                              [cand[0], cand[len(cand) // 2], cand[-1]])
            ok_("the fast station scanner is MEASURED EQUAL to the frozen reader "
                "(analyse_t16.py:340-354) at %d rows -- section 4 registers T16's OWN witness "
                "and NOT a new metric" % len(agreed), len(agreed) == 3, "L27")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # ---------------- L28 rule 4's AGE GUARD -------------------------------
        tmp = tempfile.mkdtemp(prefix="t16cage_")
        try:
            for lv in LEVELS:
                _forge_case(tmp, lv, FORGE_N[lv])
            d = os.path.join(tmp, CASES["f"])
            et = str(int(round(case_identity(d, reg)["endTime"])))
            newer = os.path.getmtime(os.path.join(d, et, "T")) + 10.0
            os.utime(os.path.join(d, "0", "T"), (newer, newer))
            out = os.path.join(tmp, "gate.json")
            code = None
            try:
                code = _selftest_grade(tmp, out, reg, limb="age-guard")
            except SystemExit as e:
                code = e.code
            ok_("rule 4 AGE GUARD: 0/T touched NEWER than the endTime fields -> REFUSE (exit %s). "
                "0/T is touched last at launch, so it dates the run allowed to produce the "
                "answer." % code, code == EXIT_REFUSE, "L28")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # ---------------- L29 rule 4's other conjuncts -------------------------
        for limb, label, mutate in (
                ("L29", "rc = 1 in STATUS -> REFUSE",
                 lambda tmp: open(os.path.join(tmp, "STATUS.%s" % CASES["f"]), "w").write(
                     "case=%s\nrc=1\ncapped=no\n" % CASES["f"])),
                ("L30", "the End line removed from log.solve (ExecutionTime lines LEFT "
                        "STANDING, so only the :511 conjunct can catch it) -> REFUSE",
                 lambda tmp: _strip_end_line(os.path.join(tmp, CASES["f"], "log.solve"))),
                ("L31", "a registered field absent at endTime -> REFUSE",
                 lambda tmp: os.remove(os.path.join(
                     tmp, CASES["f"], str(int(round(B.END_TIME["f"]))), "p_rgh")))):
            tmp = tempfile.mkdtemp(prefix="t16crule4_")
            try:
                for lv in LEVELS:
                    _forge_case(tmp, lv, FORGE_N[lv])
                mutate(tmp)
                out = os.path.join(tmp, "gate.json")
                code = None
                try:
                    code = _selftest_grade(tmp, out, reg, limb=limb)
                except SystemExit as e:
                    code = e.code
                ok_("rule 4: " + label + " (exit %s)" % code, code == EXIT_REFUSE, limb)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)

        # ---------------- L32 S8a: THE LIVE-TREE REFUSAL, DRIVEN ---------------
        # THE LIMB THIS WHOLE FILE EXISTS TO CARRY.  It is driven against the
        # REAL live root and must refuse BEFORE reading a single byte of it.
        before = len(watch_parent.hits)
        code = None
        try:
            _selftest_grade(LIVE_ROOT, os.path.join(tempfile.gettempdir(), "t16c_never.json"),
                            reg, limb="S8a-live-root")
        except SystemExit as e:
            code = e.code
        after = len(watch_parent.hits)
        good = (code == EXIT_REFUSE and after == before)
        print("      the guard fired at exit %s and the watcher recorded %d new reads under the "
              "live tree (must be 0 -- the guard runs BEFORE any read)" % (code, after - before))
        ok_("S8a LIVE-TREE REFUSAL, DRIVEN: a selftest arm pointed at the LIVE run root %s "
            "REFUSES (exit 2) and touches nothing. analyse_t18.py:509 did NOT have this guard "
            "and its side-effect json is byte-identical to the real gate_t18.json."
            % os.path.basename(LIVE_ROOT), good, "L32")

        # ---------------- L33 S8b: the sentinel ---------------------------------
        tmp = tempfile.mkdtemp(prefix="t16csent_")
        try:
            for lv in LEVELS:
                _forge_case(tmp, lv, FORGE_N[lv])
            os.remove(os.path.join(tmp, FORGE_SENTINEL))
            code = None
            try:
                _selftest_grade(tmp, os.path.join(tmp, "gate.json"), reg, limb="S8b")
            except SystemExit as e:
                code = e.code
            ok_("S8b SENTINEL: a tree with the %s marker removed is REFUSED even though its path "
                "is innocent. S8a is a path test and a symlink defeats a path test." %
                FORGE_SENTINEL, code == EXIT_REFUSE, "L33")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # ---------------- L34 S8a: a SYMLINK to the live tree -------------------
        tmp = tempfile.mkdtemp(prefix="t16clink_")
        try:
            link = os.path.join(tmp, "innocent_name")
            os.symlink(LIVE_ROOT, link)
            code = None
            try:
                _selftest_grade(link, os.path.join(tmp, "gate.json"), reg, limb="S8a-symlink")
            except SystemExit as e:
                code = e.code
            ok_("S8a resolves SYMLINKS: an innocently-named link to the live tree is REFUSED "
                "(the guard compares realpaths)", code == EXIT_REFUSE, "L34")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

        # ---------------- L35 S8d: the source detector, with its own control ----
        n_live = _unguarded_grade_calls_in_selftest()
        planted_src = _unguarded_grade_calls_in_selftest(
            "def selftest():\n    grade(HERE, 'x', 'y')\n    return 0\n")
        ok_("S8d SOURCE DETECTOR: DIRECT `grade(...)` calls inside the forge and selftest bodies "
            "= %d (every route must go through _selftest_grade, which carries S8a and S8b), and "
            "the SAME detector returns %d on a planted `grade(HERE, ...)` source -- the exact "
            "shape of analyse_t18.py:509. A zero from a detector never shown able to see a "
            "non-zero is not evidence." % (n_live, planted_src),
            (n_live == 0 and planted_src == 1), "L35")

        # ---------------- L36 no assert (L-332) ---------------------------------
        src = open(os.path.abspath(__file__)).read()
        n0 = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src)))
        n1 = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(src + "\nassert 1\n")))
        ok_("L-332: AST assert count in this file = %d (the counter sees a planted assert: %d), "
            "so every refusal fires identically under python3 -O" % (n0, n1),
            (n0 == 0 and n1 == 1), "L36")

        # ---------------- L37 the carried-over sources ARE byte-identical -------
        same, diff = _carried_over_identity()
        ok_("CARRY-OVER (frozen document section 6): %d functions and %d constants are "
            "BYTE-IDENTICAL to analyse_t16.py, measured by AST source extraction against the "
            "frozen parent rather than promised. Differing: %s"
            % (len(same), len(CARRIED_CONSTANTS), ", ".join(diff) if diff else "none"),
            not diff, "L37")

        parent_hits = sorted(set(watch_parent.hits))
        here_hits = sorted(set(watch_here.hits))

    # ---------------- L38/L39 the S8c watcher verdicts, outside the block ------
    print("  [%s] L38  S8c PLANTED CONTROL: the two watchers recorded %d and %d deliberate reads "
          "before being cleared, so a zero from them is evidence"
          % ("ok " if (planted_parent >= 1 and planted_here >= 1) else "FAIL",
             planted_parent, planted_here))
    if not (planted_parent >= 1 and planted_here >= 1):
        fails.append("L38")
    print("  [%s] L39  S8c: NO limb read anything under the live tree %s beyond the frozen "
          "instruments (%d unallowed reads), and nothing under %s (%d)"
          % ("ok " if not (parent_hits or here_hits) else "FAIL", os.path.basename(PARENT),
             len(parent_hits), os.path.basename(HERE), len(here_hits)))
    if parent_hits or here_hits:
        for h in (parent_hits + here_hits)[:10]:
            print("        UNALLOWED READ: %s" % h)
        fails.append("L39")

    # ---------------- L40 both interpreters ------------------------------------
    r = subprocess.run([sys.executable, "-O", os.path.abspath(__file__), "--selftest-inner"],
                       capture_output=True, text=True)
    ok_("under python3 -O the guards still fire (a nested probe exits %d, not 0)"
        % r.returncode, r.returncode == EXIT_REFUSE, "L40")

    print("SELFTEST %s (%d failed%s)" % ("PASS" if not fails else "FAIL", len(fails),
                                         (": " + ",".join(fails)) if fails else ""))
    return 0 if not fails else 1


# The names carried over BYTE-IDENTICALLY from analyse_t16.py, checked by AST.
CARRIED_FUNCTIONS = ("dict_value", "patch_value", "patch_vector", "latest_times",
                     "locate_internal", "read_field", "row_of", "y_centres",
                     "residual_history", "iterative_convergence", "plant",
                     "triple_of", "band_verdict")
CARRIED_CONSTANTS = ("PLANT_REL", "CONV_FLOOR", "PLAT_FLOOR", "W1_FLOOR_V", "W1_FLOOR_G",
                     "W1_FLOOR_T", "MASS_FLOOR", "G_TOL", "REFINEMENT", "DIM")


def _carried_over_identity():
    """Frozen document section 6 claims the carried-over content is
    BYTE-IDENTICAL.  This MEASURES that against the frozen parent by extracting
    each named function's source from both files' ASTs and comparing the text,
    and by comparing each carried constant's literal value.  A promise becomes a
    reading.  It is enforced HERE, in the selftest, and NOT on the grading path:
    the frozen document registers exactly ONE sha256 refusal (section 5) and
    section 9 forbids moving a gate, so this file will not add a second refusal
    that could flip a graded verdict."""
    import ast as _a
    mine = _a.parse(open(os.path.abspath(__file__)).read())
    theirs = _a.parse(open(T16_PATH).read())
    my_src = open(os.path.abspath(__file__)).read()
    their_src = open(T16_PATH).read()

    def fns(tree, src):
        return {n.name: _a.get_source_segment(src, n)
                for n in _a.walk(tree) if isinstance(n, _a.FunctionDef)}

    def consts(tree):
        out = {}
        for n in tree.body:
            if isinstance(n, _a.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], _a.Name):
                try:
                    out[n.targets[0].id] = _a.literal_eval(n.value)
                except Exception:
                    pass
        return out
    A, B_ = fns(mine, my_src), fns(theirs, their_src)
    CA, CB = consts(mine), consts(theirs)
    same, diff = [], []
    for name in CARRIED_FUNCTIONS:
        if name in A and name in B_ and A[name] == B_[name]:
            same.append(name)
        else:
            diff.append("fn:" + name)
    for name in CARRIED_CONSTANTS:
        if name in CA and name in CB and CA[name] == CB[name]:
            same.append(name)
        else:
            diff.append("const:%s (%r vs %r)" % (name, CA.get(name), CB.get(name)))
    return same, diff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-inner", action="store_true",
                    help="a single S8a probe, used by the -O limb")
    ap.add_argument("--root", default=None, help="run tree")
    ap.add_argument("--json", default=os.path.join(HERE, "gate_t16c.json"))
    a = ap.parse_args()
    if a.selftest_inner:
        _selftest_root_guard(LIVE_ROOT, "-O probe")
        return EXIT_OK
    if a.selftest:
        return selftest()
    reg = load_registered()
    root = os.path.abspath(a.root) if a.root else LIVE_ROOT
    return grade(root, a.json, reg)


if __name__ == "__main__":
    sys.exit(main())
