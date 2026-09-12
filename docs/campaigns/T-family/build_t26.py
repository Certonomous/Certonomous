#!/usr/bin/env python3
"""
T26 CASE BUILDER -- stages into `0.orig/` and NEVER creates `0/`.

REGISTERED PATH: T26_PREREGISTRATION.md:801.  Written here, not under
`verification/runs/T-family/T26_runs/`, because :106 makes that directory's
ABSENCE the rule-2 pre-compute condition of the registration.

WHY `0.orig/` AND NEVER `0/` -- THE WHOLE POINT OF THIS FILE.
The supervisor's finding of 2026-09-10: clause 7 (`refuse a case where 0/ or a
time directory already exists`) is DEFINED in seven K0-family instruments and
CALLED BY ZERO LAUNCHERS, because EVERY BUILDER CREATED `0/` ITSELF.  With `0/`
always present at launch, "refuse if 0/ exists" could never fire on a
legitimate launch -- seven dead levers, and the guard that was supposed to
protect the age guard protected nothing.

The repair is a DESIGN, not a hope, and it is split across three files:
  * THIS ONE stages the initial fields into `0.orig/` and REFUSES (exit 2) if
    `0/` already exists.  It never writes `0/`.
  * `launch_t26.sh` creates `0` from `0.orig` and touches `0/fluid/T` LAST, so
    that file dates the run allowed to produce the answer (clause 6).
  * `mark_done_t26.py --launch-guard` is the ONLY place the rule is written
    down; both launch sites CALL it and neither reimplements it (rule 14).
Pattern from `scripts/build_k0h.py:1100-1147`, cited by the registration :635.

REFUSALS (exit 2), never a degrade:
  * `0/` exists                      -- clause 7's precondition already broken
  * a numeric time directory exists  -- the case has already run
  * `0.orig/fluid/T` was not written -- the age-guard referent would be absent
  * the registered field set is incomplete in `0.orig/`

Usage:  python3 build_t26.py --case-dir DIR [--level L1|L2|L3]
        python3 build_t26.py --selftest
"""
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = ("L1", "L2", "L3")
FLUID_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega")
SOLID_FIELDS = ("T", "p")
SOLID_REGIONS = ("core", "housing", "duct")
AGE_REF = os.path.join("0.orig", "fluid", "T")

# registered operating point, T26_PREREGISTRATION.md:383
U_INF = 20.000
T_AMBIENT = 300.0
P_LOSS_W = 305.0
EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    return EXIT_REFUSE


def preflight(case_dir):
    """Return refusal reasons; EMPTY means the case may be staged."""
    why = []
    if os.path.exists(os.path.join(case_dir, "0")):
        why.append("%s already has a 0/ -- THIS BUILDER NEVER CREATES 0/, so one "
                   "that exists came from elsewhere. Staging over it would leave "
                   "clause 7 with nothing to refuse and the age guard with a "
                   "referent this run did not write." % case_dir)
    if os.path.isdir(case_dir):
        for name in sorted(os.listdir(case_dir)):
            if (re.fullmatch(r"[0-9]+(\.[0-9]+)?", name) and float(name) > 0
                    and os.path.isdir(os.path.join(case_dir, name))):
                why.append("%s already has time directory %s -- this case has "
                           "already run" % (case_dir, name))
    return why


def stage(case_dir, level, overwrite_orig=False):
    """Write the registered initial fields into 0.orig/ and nowhere else."""
    orig = os.path.join(case_dir, "0.orig")
    if os.path.isdir(orig) and not overwrite_orig:
        return refuse("%s already exists; pass --overwrite-orig to restage. A "
                      "silent restage would change the fields a launched run "
                      "started from." % orig)
    if os.path.isdir(orig):
        shutil.rmtree(orig)
    os.makedirs(os.path.join(orig, "fluid"), exist_ok=True)
    for reg in SOLID_REGIONS:
        os.makedirs(os.path.join(orig, reg), exist_ok=True)

    # The fluid fields.  Values are the registered operating point; the
    # wall treatment is the ONE registered choice for every wall at every
    # level (nutUSpalding + alphatJayatilleke, registration :407-411), so the
    # rung never silently switches treatment between patches or levels.
    for f in FLUID_FIELDS:
        _write_field(os.path.join(orig, "fluid", f), f)
    for reg in SOLID_REGIONS:
        for f in SOLID_FIELDS:
            _write_field(os.path.join(orig, reg, f), f, solid=True)

    # The age-guard referent must exist in 0.orig, or launch_t26.sh has
    # nothing to copy and touch last.
    if not os.path.isfile(os.path.join(case_dir, AGE_REF)):
        return refuse("%s was not written -- launch_t26.sh touches 0/fluid/T LAST "
                      "as the age-guard referent (clause 6) and cannot do so if "
                      "0.orig/fluid/T does not exist" % AGE_REF)
    miss = [f for f in FLUID_FIELDS
            if not os.path.isfile(os.path.join(orig, "fluid", f))]
    for reg in SOLID_REGIONS:
        miss += ["%s/%s" % (reg, f) for f in SOLID_FIELDS
                 if not os.path.isfile(os.path.join(orig, reg, f))]
    if miss:
        return refuse("the registered field set is incomplete in 0.orig: %s"
                      % ",".join(miss))
    if os.path.exists(os.path.join(case_dir, "0")):
        return refuse("a 0/ appeared during staging -- this builder never creates "
                      "one, so something else is writing into %s" % case_dir)
    print("staged %s for level %s: 0.orig/ only, NO 0/ created (clause 7 is left "
          "something to refuse)" % (case_dir, level))
    return EXIT_OK


_DIMS = {"T": "[0 0 0 1 0 0 0]", "U": "[0 1 -1 0 0 0 0]",
         "p_rgh": "[1 -1 -2 0 0 0 0]", "p": "[1 -1 -2 0 0 0 0]",
         "alphat": "[1 -1 -1 0 0 0 0]", "nut": "[0 2 -1 0 0 0 0]",
         "k": "[0 2 -2 0 0 0 0]", "omega": "[0 0 -1 0 0 0 0]"}
_INIT = {"T": T_AMBIENT, "U": U_INF, "p_rgh": 0.0, "p": 101325.0,
         "alphat": 0.0, "nut": 0.0, "k": 1.5 * (0.05 * U_INF) ** 2,
         "omega": 1.0}


def _write_field(path, name, solid=False):
    vec = (name == "U")
    val = _INIT[name]
    with open(path, "w") as fh:
        fh.write("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
                 "    class       vol%sField;\n    object      %s;\n}\n"
                 % ("Vector" if vec else "Scalar", name))
        fh.write("dimensions      %s;\n" % _DIMS[name])
        fh.write("internalField   uniform %s;\n"
                 % (("(%g 0 0)" % val) if vec else repr(float(val))))
        fh.write("boundaryField\n{\n    \".*\"\n    {\n"
                 "        type            %s;\n        value           uniform %s;\n"
                 "    }\n}\n" % ("zeroGradient" if solid else "calculated",
                                 ("(%g 0 0)" % val) if vec else repr(float(val))))


def selftest():
    import ast
    import tempfile
    print("build_t26.py --selftest")
    print("=" * 74)
    fails = []
    tmp = tempfile.mkdtemp(prefix="t26_build_")
    try:
        clean = os.path.join(tmp, "clean")
        os.makedirs(clean)
        rc = stage(clean, "L1")
        made_0 = os.path.exists(os.path.join(clean, "0"))
        has_orig = os.path.isfile(os.path.join(clean, AGE_REF))
        ok = rc == EXIT_OK and not made_0 and has_orig
        print("  [%s] CONTROL: clean case staged -> rc %d, 0/ created: %s, "
              "0.orig/fluid/T present: %s" % ("ok " if ok else "BAD", rc, made_0, has_orig))
        if not ok:
            fails.append("clean stage")

        print("  [%s] THE INVARIANT: this builder created NO 0/ -- so clause 7 has "
              "something to refuse" % ("ok " if not made_0 else "BAD"))

        d0 = os.path.join(tmp, "dirty0")
        os.makedirs(os.path.join(d0, "0"))
        w = preflight(d0)
        ok = bool(w) and "0/" in w[0]
        print("  [%s] MUTATION: 0/ pre-existing -> preflight REFUSES" % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("dirty 0/")

        dt = os.path.join(tmp, "dirtyT")
        os.makedirs(os.path.join(dt, "1200"))
        w = preflight(dt)
        ok = bool(w) and "1200" in w[0]
        print("  [%s] MUTATION: time directory 1200/ -> preflight REFUSES" % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("dirty time")

        w = preflight(clean)
        ok = (w == [])
        print("  [%s] NEGATIVE CONTROL: the clean staged case still passes preflight "
              "(the refusals above are the 0//time dirs, not staging itself)"
              % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("clean preflight")

        rc = stage(clean, "L1")
        ok = rc == EXIT_REFUSE
        print("  [%s] MUTATION: restaging over an existing 0.orig/ without "
              "--overwrite-orig -> REFUSE" % ("ok " if ok else "BAD"))
        if not ok:
            fails.append("restage")

        # The registered field set must be COMPLETE, and its absence caught.
        os.remove(os.path.join(clean, "0.orig", "fluid", "omega"))
        miss = [f for f in FLUID_FIELDS
                if not os.path.isfile(os.path.join(clean, "0.orig", "fluid", f))]
        ok = miss == ["omega"]
        print("  [%s] MUTATION: a registered field removed -> the completeness check "
              "sees exactly %s" % ("ok " if ok else "BAD", miss))
        if not ok:
            fails.append("field set")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n_assert = sum(isinstance(x, ast.Assert)
                   for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] NO `assert` in this file: AST count = %d (counter sees planted: %d)"
          % ("ok " if ok else "BAD", n_assert, planted))
    if not ok:
        fails.append("ast")

    print("=" * 74)
    print("SELFTEST %s (%d failed)%s" % ("PASS" if not fails else "FAIL", len(fails),
                                         "" if not fails else ": " + "; ".join(fails)))
    return EXIT_OK if not fails else 1


# ===========================================================================
# THE MESH INSTRUMENT -- added 2026-09-11, PRE-FIRST-COMPUTE.
#
# THE DEFECT IT CLOSES, stated as section 21.14 item 1 states it:
# "`blockMesh`, `snappyHexMesh`, `surfaceFeatureExtract`, `splitMeshRegions`
#  and `topoSet` appear ZERO times in `build_t26.py`, `launch_t26.sh` and
#  `orchestrate_t26.py` ... THE CHAIN REQUIRES A MESH NO MEMBER OF THE CHAIN
#  CREATES.  section 3.6 registers a per-level BIRTH certificate 'written by
#  build_t26.py' and `BIRTH`/`certificate` appear ZERO times in that file."
#
# WHY IT IS IN *THIS* FILE AND NOT A NEW ONE.  Two registered reasons, neither
# a preference:
#   1. section 3.6 registers the birth certificate as "written by
#      `build_t26.py`".  A certificate written by some other file would satisfy
#      the words of nothing.
#   2. `analyse_t26.py`'s REQUIRED_INSTRUMENTS pins exactly five files.  A NEW
#      repository instrument would be UNPINNED, and the freeze check would
#      cover four of five while its registration claimed all five -- which is
#      verbatim the K2f defect that check's own comment names.  The only way to
#      add mesh code under the existing pin set is to add it to a pinned file.
#   THE DETACHED DRIVER IS GENERATED INTO THE MESH DIRECTORY AT RUN TIME, for
#   the same reason: a generated artifact needs no pin, a new .sh would.
#
# WHAT IT HOLDS NO COPY OF (section 21 ruling 5).  Delta_0, endTime, ranks and
# cell counts come from `analyse_t26.read_registered_ladder()` -- the SAME
# function the grader uses, not a second implementation of it (`CLAUDE.md`
# rule 14).  Surface levels, layer counts, Delta_1, the region names, the
# domain planes, the core inset, the STL sha256 and the two registered output
# paths are PARSED from the registration at every call.  Every parse REFUSES
# when its anchor is absent and DEFAULTS NOTHING: a defaulted registered value
# is the private copy this section exists to remove, wearing a hat.
#
# THE TWO CONTROLS THE SUPERVISOR MADE BINDING, and where they are driven:
#   * THE BIRTH CERTIFICATE IS PRODUCED **AND READ**, by `read_certificate()`,
#     which REFUSES on absent / unparseable / structurally incomplete / value-
#     mismatched, and is CALLED BY THE BUILD ITSELF (`certify()` reads back
#     what it just wrote and refuses if the reader will not accept it).  Every
#     refusal arm is driven in `mesh_selftest()` AGAINST A LIVE POSITIVE ARM --
#     a reader never shown accepting a good certificate has not been shown able
#     to reject a bad one.  A certificate nothing reads is the
#     freeze-verifies-bytes-never-call-sites defect one layer on.
#   * THE REGION SPLIT IS COUNTED AGAINST THE REGISTRATION, not against a
#     constant.  `check_regions()` reads the four region names out of
#     section 3.1 and refuses a built tree that carries any other set.  The
#     three-where-four-are-registered arm is driven.
# ===========================================================================
import json
import math
import struct
import subprocess
import time

# The registration is the authority for every registered quantity below.
REGISTRATION = os.path.join(HERE, "T26_PREREGISTRATION.md")

#: `CLAUDE.md` rule 3.  Every reader in this section that can return a zero,
#: an empty set or an absence is driven in BOTH directions in mesh_selftest().
EXIT_CONTROL_FAILED = 3


class Refused(Exception):
    """Raised by a parse or a check that will not degrade.  main() turns it
    into exit 2 with the reason printed; never caught to continue."""


def _reg_text(path=None):
    p = path or REGISTRATION
    if not os.path.isfile(p):
        raise Refused("no registration at %s -- every registered quantity in "
                      "the mesh instrument is READ from it and none is "
                      "defaulted (section 21 ruling 5)" % p)
    return open(p, "r", errors="replace").read()


def _num(s):
    """Parse a number that may carry a UNICODE MINUS (U+2212) or thin spaces.

    The registration's section 3.2 writes the inlet plane as
    `x = **-0.175000 m**` with U+2212, not ASCII '-'.  A parser that misses
    that reads a POSITIVE inlet plane and builds a box that does not contain
    the domain.  Normalisation is done here, once, and driven."""
    s = (s.replace("−", "-").replace("–", "-").replace("—", "-")
          .replace(" ", "").replace(" ", "").replace(",", "").strip())
    return float(s)


# ---------------------------------------------------------------------------
# REGISTERED QUANTITIES, READ.  One function per quantity; each names the
# section it reads and REFUSES rather than defaulting.
# ---------------------------------------------------------------------------

def _last(pattern, text, what, flags=0):
    """The LAST match in the registration, never the first.

    DOCUMENT ORDER IS SUPERSESSION ORDER on this rung -- `analyse_t26.py`'s
    freeze checker states the same rule for the instrument pins ("IT READS THE
    LAST PIN FOR EACH FILE, not the first ... Document order IS supersession
    order").  It matters here for a measured reason: this instrument's own
    internal-consistency check REFUSED on its first run because the parser had
    read section 3.4's `duct-bore surface level` row -- 1 (4.000 mm), on the
    Delta_0 = 8.000 mm ladder section 21.4 STRUCK -- instead of section 21.4's
    1 (9.000 mm).  A first-match parser reads the superseded ladder and cannot
    tell.  A section-name anchor would have been just as wrong the next time a
    section supersedes section 21.4.  REFUSES when there is no match at all;
    absence is never a default."""
    hits = list(re.finditer(pattern, text, flags))
    if not hits:
        raise Refused("the registration carries no %s" % what)
    return hits[-1]


def reg_stl_sha256(text=None):
    """The registered surface's sha256 -- section 1, printed in full at :135."""
    t = text if text is not None else _reg_text()
    return _last(r"\*\*sha256\*\*\s*`([0-9a-f]{64})`", t,
                 "full 64-hex sha256 for the surface (section 1); the surface "
                 "is pinned or it is not used, never taken on trust").group(1)


def reg_regions(text=None):
    """The REGISTERED region names -- section 3.1's table, first column.

    THIS IS THE BASIS OF THE REGION-SPLIT CONTROL.  The count four is not
    written down in this file; it is whatever section 3.1 registers, so a
    registration that moved to three or five regions moves the check with it
    and a build that silently delivers a different set is REFUSED."""
    t = text if text is not None else _reg_text()
    m = _last(r"^### 3\.1 Regions.*?^### 3\.2 ", t,
              "section 3.1 Regions table; the registered region set is then "
              "unknowable and this instrument does not invent one",
              re.M | re.S)
    rows = re.findall(r"^\|\s*`([A-Za-z_][A-Za-z0-9_]*)`\s*\|", m.group(0), re.M)
    out = []
    for r in rows:
        if r not in out:
            out.append(r)
    if len(out) < 2:
        raise Refused("section 3.1's table yielded %d region name(s) -- a "
                      "region table that does not parse is a REFUSAL, never a "
                      "default" % len(out))
    return out


def reg_domain_x(text=None):
    """The inlet and outlet planes -- section 3.2's table."""
    t = text if text is not None else _reg_text()
    pat = (r"^\|\s*%s plane\s*\|\s*x\s*=\s*\*\*([^*]+?)\s*m\*\*")
    vals = {}
    for which in ("inlet", "outlet"):
        vals[which] = _num(_last(pat % which, t,
                                 "section 3.2 %s plane" % which, re.M).group(1))
    if not vals["inlet"] < vals["outlet"]:
        raise Refused("section 3.2's inlet plane %.6f is not upstream of its "
                      "outlet plane %.6f -- this is the unicode-minus parse "
                      "failure, caught rather than built on"
                      % (vals["inlet"], vals["outlet"]))
    return vals["inlet"], vals["outlet"]


def reg_core_inset(text=None):
    """The core inset -- section 3.1's `core` row, 'hub interior inset X mm'."""
    t = text if text is not None else _reg_text()
    return _num(_last(r"hub interior inset\s+([0-9.]+)\s*mm", t,
                      "'hub interior inset N mm' for `core` (section 3.1); the "
                      "synthesised offset is not guessed").group(1)) / 1000.0


def reg_surface_levels(text=None):
    """Per-level surface refinement levels -- section 21.4's table.

    Returns {level: {'duct': l, 'hub': l, 'strut': l}}.

    A CONTROL ON THE REGISTRATION ITSELF, not only on the parse: section 21.4
    prints each level BOTH as an octree level and as a millimetre size, e.g.
    `4 (1.1250 mm)`.  Those two must satisfy mm == Delta_0 / 2**level for the
    Delta_0 the SAME document registers on its REGISTERED-LADDER line.  If they
    do not, the registration disagrees with itself and this instrument REFUSES
    rather than choosing which half to believe."""
    t = text if text is not None else _reg_text()
    ladder = read_registered_ladder(REGISTRATION)
    order = sorted(ladder)                      # L1, L2, L3 -- from the ladder
    rows = {"duct": r"duct-bore surface level", "hub": r"hub surface level",
            "strut": r"\*\*strut surface level\*\*"}
    out = dict((lv, {}) for lv in order)
    for key, label in rows.items():
        m = _last(r"^\|\s*%s\s*\|(.+)\|\s*$" % label, t,
                  "'%s' surface-level row; surface levels are read, never "
                  "assumed" % key, re.M)
        got = re.findall(r"([0-9]+)\s*\(\s*([0-9.]+)\s*mm\s*\)", m.group(1))
        if len(got) != len(order):
            raise Refused("section 21.4's '%s' row parses to %d entries for %d "
                          "registered levels" % (key, len(got), len(order)))
        for lv, (lev, mm) in zip(order, got):
            lev, mm = int(lev), _num(mm)
            want = ladder[lv]["delta0_mm"] / (2.0 ** lev)
            if abs(mm - want) > 5e-4:
                raise Refused(
                    "REGISTRATION INTERNALLY INCONSISTENT: section 21.4 gives "
                    "%s at %s as level %d AND as %.4f mm, but that level on "
                    "Delta_0 = %.3f mm (the REGISTERED-LADDER line for %s) is "
                    "%.4f mm. Two registered numbers for one quantity is a "
                    "refusal, not a choice."
                    % (key, lv, lev, mm, ladder[lv]["delta0_mm"], lv, want))
            out[lv][key] = lev
    return out


def reg_layers(text=None):
    """Layer counts -- section 21.4's 'layers (hub / strut / duct)' row."""
    t = text if text is not None else _reg_text()
    m = _last(r"^\|\s*layers \(hub / strut / duct\)\s*\|(.+)\|\s*$", t,
              "layer-count row", re.M)
    trip = re.findall(r"([0-9]+)\s*/\s*([0-9]+)\s*/\s*([0-9]+)", m.group(1))
    if not trip:
        raise Refused("section 21.4's layer row does not parse as h/s/d triples")
    if len(set(trip)) != 1:
        raise Refused("section 21.4 registers DIFFERENT layer counts per level "
                      "%s; section 3.4 registers them held fixed. Refused."
                      % (sorted(set(trip)),))
    h, s, d = trip[0]
    return {"hub": int(h), "strut": int(s), "duct": int(d)}


def reg_delta1(text=None):
    """Near-wall first-cell thickness, hub/strut and duct -- section 3.3."""
    t = text if text is not None else _reg_text()
    wall = _num(_last(r"\*\*first-cell THICKNESS\*\*.*?\*\*([0-9.e+-]+)\s*m\s*=",
                      t, "first-cell thickness (section 3.3)").group(1))
    duct = _num(_last(r"duct-bore.{0,6}at y.{0,4}=\s*30.*?\*\*([0-9.eE+-]+)\s*m\*\*",
                      t, "duct-bore first-cell thickness (section 3.3)").group(1))
    return {"wall": wall, "duct": duct}


def reg_mesh_root(text=None):
    """Where built polyMesh trees live -- section 21.11, OUTSIDE the repository."""
    t = text if text is not None else _reg_text()
    return _last(r"live OUTSIDE the repository, under[\s>]*`([^`<]+)<level>/`",
                 t, "mesh root (section 21.11); this instrument does not choose "
                    "where megabytes land").group(1)


def reg_certificate_path(text=None):
    """Where the birth certificate lands -- section 3.6, INSIDE the repository."""
    t = text if text is not None else _reg_text()
    m = _last(r"`(verification/runs/[^`<]*)<level>/(MESH_BIRTH_CERTIFICATE\.json)`",
              t, "birth-certificate path (section 3.6)")
    return m.group(1), m.group(2)


def reg_component_measurements(text=None):
    """section 21.12's independent reproduction line: the per-component facet
    counts, signed volumes and areas the STL split must reproduce.

    This is what makes the index split SAFE.  section 21.12: the facets are
    contiguous by component in file order "so the split is deterministic AND IS
    ASSERTED AGAINST PER-COMPONENT VOLUME AND BBOX, NEVER TRUSTED FROM ORDER"."""
    t = text if text is not None else _reg_text()
    m = _last(r"facets\s+([0-9,]+)\s*/\s*([0-9,]+)\s*/\s*([0-9,]+)\s*/\s*"
                  r"([0-9,]+)\s*/\s*([0-9,]+)\s*;\s*volumes\s+"
                  r"([+-][0-9.e+-]+),\s*([+-][0-9.e+-]+),\s*([+-][0-9.e+-]+)"
                  r"\s*.3\s*;\s*areas\s+([0-9.]+)\s*/\s*([0-9.]+)\s*/\s*([0-9.]+)", t,
              "parseable per-component reproduction line (section 21.12); the "
              "index split would then be trusted from file order, which "
              "section 21.12 forbids")
    g = m.groups()
    return {
        "hub":    dict(facets=int(g[0].replace(",", "")), vol=_num(g[5]), area=_num(g[8])),
        "duct":   dict(facets=int(g[1].replace(",", "")), vol=_num(g[6]), area=_num(g[9])),
        "strutA": dict(facets=int(g[2].replace(",", "")), vol=_num(g[7]), area=_num(g[10])),
        "strutB": dict(facets=int(g[3].replace(",", "")), vol=_num(g[7]), area=_num(g[10])),
        "strutC": dict(facets=int(g[4].replace(",", "")), vol=_num(g[7]), area=_num(g[10])),
    }


def read_registered_ladder(path=None):
    """The registered ladder, via THE GRADER'S OWN READER.

    `analyse_t26.read_registered_ladder()` is imported and called; it is NOT
    reimplemented here.  `CLAUDE.md` rule 14 -- a lesson is not applied until
    EVERY call site asserts it -- and section 21.7's finding on this very rung:
    a second private copy of the ladder is a second place for the ladder to be
    wrong, and last time it would have read every level at the endTime of the
    level ABOVE it.  If that module refuses, it exits 2 with its own reason;
    this wrapper does not soften that."""
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    try:
        import analyse_t26
    except Exception as exc:                        # noqa: BLE001 - reported
        raise Refused("analyse_t26 is not importable (%s: %s); the ladder is "
                      "READ by the grader's own reader and this file keeps no "
                      "copy to fall back on" % (type(exc).__name__, exc))
    return analyse_t26.read_registered_ladder(path or REGISTRATION)


# ---------------------------------------------------------------------------
# THE SURFACE.  Read from the REGISTERED BINARY STL, synthesised, never
# inherited (section 21.12: the named-solid ASCII copy under
# certonomous-runs/T26_mesh_dev/surface/ is sha256 547c3613..., NOT the
# registered 131aab8e..., "A file identical in every respect we checked is
# still not the file the registration pins.")
# ---------------------------------------------------------------------------

def _np():
    try:
        import numpy
    except ImportError:
        raise Refused("numpy is not importable; the surface synthesis is "
                      "arithmetic on 6,288 facets and is not done by hand")
    return numpy


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_binary_stl(path):
    """Facets as an (n,3,3) float64 array, from the binary STL at `path`."""
    np = _np()
    raw = open(path, "rb").read()
    if len(raw) < 84:
        raise Refused("%s is too short to be a binary STL" % path)
    n = struct.unpack("<I", raw[80:84])[0]
    if len(raw) != 84 + 50 * n:
        raise Refused("%s declares %d facets but is %d bytes, not %d -- this is "
                      "not the binary STL it claims to be"
                      % (path, n, len(raw), 84 + 50 * n))
    buf = np.frombuffer(raw[84:], dtype=np.uint8).reshape(n, 50)
    tris = np.ascontiguousarray(buf[:, 12:48]).view("<f4").reshape(n, 3, 3)
    return tris.astype(np.float64)


def signed_volume(t):
    np = _np()
    return float(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum() / 6.0)


def surface_area(t):
    np = _np()
    return float(0.5 * np.linalg.norm(np.cross(t[:, 1] - t[:, 0],
                                               t[:, 2] - t[:, 0]), axis=1).sum())


def surface_parts(tris, tol=9):
    """Connected components of a triangle soup, by shared (rounded) vertex.

    THIS IS THE CHECK THE PROBE OF 2026-09-11 PAID 16 CORE-MINUTES TO DISCOVER.
    `cellZoneInside inside` needs a searchable volume, and a geometry entry that
    bundles FIVE disconnected closed bodies cannot supply one.  The probe wrote
    hub+duct+strutA/B/C into ONE `triSurfaceMesh` named `motor` with the
    cellZones in its `regions{}` sub-dict; snappyHexMesh reported "Found 2
    closed, named surfaces" against THREE geometry entries supplied, fell back
    to the seed WALK for everything on `motor`, and the walk leaked."""
    np = _np()
    parent = list(range(len(tris)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    key = {}
    for i, t in enumerate(tris):
        for v in t:
            k = (round(float(v[0]), tol), round(float(v[1]), tol), round(float(v[2]), tol))
            j = key.setdefault(k, i)
            ra, rb = find(j), find(i)
            if ra != rb:
                parent[rb] = ra
    return len(set(find(i) for i in range(len(tris))))


def split_components(tris, want):
    """The five registered components, by CONTIGUOUS FILE ORDER, then ASSERTED.

    section 21.12 registers the order (duct [0,768), hub [768,6144), struts at
    6144 / 6192 / 6240) AND registers that it "is asserted against per-component
    volume and bbox, NEVER TRUSTED FROM ORDER".  Both halves are here: the
    ranges are derived from the registered facet counts, and every component is
    then checked against the registered signed volume and area before the split
    is used for anything.  A mismatch is a REFUSAL."""
    np = _np()
    order = ("duct", "hub", "strutA", "strutB", "strutC")
    total = sum(want[k]["facets"] for k in order)
    if len(tris) != total:
        raise Refused("the surface carries %d facets; section 21.12 registers "
                      "%d across its five components" % (len(tris), total))
    out, i = {}, 0
    for name in order:
        n = want[name]["facets"]
        out[name] = dict(tris=tris[i:i + n], lo=i, hi=i + n)
        i += n
    bad = []
    for name in order:
        c = out[name]
        v, a = signed_volume(c["tris"]), surface_area(c["tris"])
        c["vol"], c["area"] = v, a
        c["bbox"] = (c["tris"].reshape(-1, 3).min(0).tolist(),
                     c["tris"].reshape(-1, 3).max(0).tolist())
        if abs(v - want[name]["vol"]) > 1e-9:
            bad.append("%s signed volume %+.6e vs registered %+.6e"
                       % (name, v, want[name]["vol"]))
        if abs(a - want[name]["area"]) > 1e-6:
            bad.append("%s area %.6f vs registered %.6f" % (name, a, want[name]["area"]))
        if v <= 0.0:
            bad.append("%s signed volume is not positive -- GEO-4's condition" % name)
    if bad:
        raise Refused("THE INDEX SPLIT DOES NOT REPRODUCE section 21.12's "
                      "MEASUREMENTS, so file order is NOT the component order "
                      "here and the split is refused rather than trusted: "
                      + "; ".join(bad))
    return out


def hub_profile(hub_tris, tol=1e-6):
    """The hub's meridional profile, MEASURED: (x, r) per axial station.

    Refuses unless the hub really is a polygon of revolution -- at every
    station all vertex radii must agree (section 21.12 measured them equal to
    1e-9 m).  A 4 mm offset of something that is not a body of revolution is
    not the registered `core`."""
    np = _np()
    pts = hub_tris.reshape(-1, 3)
    r = np.hypot(pts[:, 1], pts[:, 2])
    xs = np.unique(np.round(pts[:, 0], 9))
    prof, spread = [], 0.0
    for x in xs:
        sel = np.abs(pts[:, 0] - x) < tol
        rr = r[sel]
        spread = max(spread, float(rr.max() - rr.min()))
        prof.append((float(x), float(rr.mean())))
    if spread > 1e-7:
        raise Refused("the hub is NOT a polygon of revolution: the widest "
                      "radius spread at a single axial station is %.3e m. "
                      "section 21.12's inset is registered on a 96-gon of "
                      "revolution." % spread)
    prof.sort()
    return prof, spread


def gon_azimuths(comp_tris, radius, tol=1e-6):
    """The MEASURED azimuths of a polygon-of-revolution's vertices at `radius`.

    THE PHASE IS NEVER ASSUMED.  section 21.12 registers that the hub and the
    duct bore "share one 96-gon phase and 0 deg / +-120 deg are vertices of
    both"; the synthesised surfaces take their phase from THIS measurement of
    the registered file, so a phase error cannot be introduced by a constant."""
    np = _np()
    pts = comp_tris.reshape(-1, 3)
    rr = np.hypot(pts[:, 1], pts[:, 2])
    sel = pts[np.abs(rr - radius) < tol]
    if len(sel) == 0:
        raise Refused("no vertex of this component lies at radius %.6f +- %g -- "
                      "the phase cannot be measured and is not guessed"
                      % (radius, tol))
    th = np.sort(np.unique(np.round(np.arctan2(sel[:, 2], sel[:, 1]), 7)))
    if len(th) < 3:
        raise Refused("only %d distinct azimuths at radius %.6f" % (len(th), radius))
    d = np.diff(np.append(th, th[0] + 2 * math.pi))
    if float(d.max() - d.min()) > 1e-5:
        raise Refused("the vertex azimuths at radius %.6f are not uniformly "
                      "spaced (spread %.3e rad); this is not a regular polygon "
                      "of revolution" % (radius, float(d.max() - d.min())))
    return th.tolist(), float(d.mean())


def miter_offset_profile(prof, d):
    """The inward offset of a convex meridional profile by `d`, by MITERING.

    WHY MITER AND NOT A DISTANCE FIELD.  section 21.12 established the property
    that makes mitering exact here: "All 28 meridional turn angles carry the
    same sign ... so the profile is convex throughout and the erosion boundary
    is a simple curve WITH NO INTERIOR CUSP".  That convexity is RE-CHECKED
    here rather than inherited, and a profile that fails it is REFUSED -- on a
    non-convex profile the miter offset self-intersects and would silently
    emit a surface with inverted facets.

    The two tips sit ON the axis, where the profile has no second neighbour.
    They are handled by MIRRORING the profile through the axis into a closed
    convex polygon, so one code path serves tips and flanks alike; this is
    also why both tips recede by MORE than `d` (section 21.12 measured nose
    4.0385 mm and tail 4.0558 mm for a 4.000 mm inset -- "both exceed 4 mm
    because both ends taper")."""
    np = _np()
    P = np.array(prof, dtype=float)
    if P[0][1] > 1e-9 or P[-1][1] > 1e-9:
        raise Refused("the meridional profile does not start and end on the "
                      "axis (r = %.3e, %.3e); the mirror closure is invalid"
                      % (P[0][1], P[-1][1]))
    # closed convex polygon: profile forward (r >= 0) then mirrored backward
    poly = np.vstack([P, np.column_stack([P[-2:0:-1, 0], -P[-2:0:-1, 1]])])
    n = len(poly)
    e = np.roll(poly, -1, axis=0) - poly                  # edge i: poly[i]->poly[i+1]
    L = np.linalg.norm(e, axis=1)
    if float(L.min()) <= 0.0:
        raise Refused("the meridional profile carries a zero-length segment")
    u = e / L[:, None]
    # inward normal of edge i for a CCW-in-(x,r) traversal of the closed polygon
    nin = np.column_stack([-u[:, 1], u[:, 0]])
    area2 = float(np.sum(poly[:, 0] * np.roll(poly[:, 1], -1)
                         - np.roll(poly[:, 0], -1) * poly[:, 1]))
    if area2 < 0:
        nin = -nin
    cross = u[:, 0] * np.roll(u, -1, axis=0)[:, 1] - u[:, 1] * np.roll(u, -1, axis=0)[:, 0]
    turn = cross * (1.0 if area2 >= 0 else -1.0)
    nonconvex = int(np.sum(turn < -1e-12))
    if nonconvex:
        raise Refused("the meridional profile turns the wrong way at %d of its "
                      "%d vertices -- it is NOT convex, so the miter offset "
                      "would self-intersect and section 21.12's 'no interior "
                      "cusp' does not hold for this surface" % (nonconvex, n))
    out = []
    for i in range(n):
        a, b = nin[(i - 1) % n], nin[i]          # edges meeting AT vertex i
        m = a + b
        Lm = float(np.linalg.norm(m))
        if Lm < 1e-12:
            raise Refused("a 180-degree reversal at meridional vertex %d" % i)
        m = m / Lm
        denom = float(m.dot(b))
        if denom <= 1e-9:
            raise Refused("degenerate miter at meridional vertex %d" % i)
        out.append(poly[i] + m * (d / denom))
    out = np.array(out)
    keep = out[out[:, 1] >= -1e-12]                # the upper half is the profile
    keep = keep[np.argsort(keep[:, 0])]
    # collapse the mirrored tips onto the axis exactly
    keep[0, 1] = max(keep[0, 1], 0.0)
    keep[-1, 1] = max(keep[-1, 1], 0.0)
    if len(keep) < 3:
        raise Refused("the %.4f m inset consumed the profile (only %d points "
                      "survive); the core would be degenerate"
                      % (d, len(keep)))
    if float(keep[:, 1].max()) <= 0.0:
        raise Refused("the %.4f m inset leaves no positive radius anywhere; the "
                      "core is empty" % d)
    return keep


def revolve(prof, azimuths, cap_ends=True):
    """A closed polygon-of-revolution surface from a meridional profile.

    Outward normals, checked by signed volume at the call site."""
    np = _np()
    P = np.asarray(prof, dtype=float)
    th = np.asarray(azimuths, dtype=float)
    c, s = np.cos(th), np.sin(th)
    tris = []
    for i in range(len(P) - 1):
        (x0, r0), (x1, r1) = P[i], P[i + 1]
        for j in range(len(th)):
            k = (j + 1) % len(th)
            a = (x0, r0 * c[j], r0 * s[j]); b = (x0, r0 * c[k], r0 * s[k])
            d = (x1, r1 * c[j], r1 * s[j]); e = (x1, r1 * c[k], r1 * s[k])
            # Winding OUTWARD.  The first draft of this loop wound the
            # lateral facets INWARD and the signed-volume check at the call
            # site caught it at -3.501282e-04 -- the check earning its place:
            # an inward-wound `core.stl` is a perfectly valid closed surface
            # that snappyHexMesh would read as the COMPLEMENT of the core.
            if r0 > 1e-12 and r1 > 1e-12:
                tris.append([a, e, d]); tris.append([a, b, e])
            elif r0 <= 1e-12 < r1:                    # cone tip at x0
                tris.append([a, e, d])
            elif r1 <= 1e-12 < r0:                    # cone tip at x1
                tris.append([a, b, e])
    if cap_ends:
        for (x, r), sgn in ((P[0], -1.0), (P[-1], +1.0)):
            if r <= 1e-12:
                continue
            for j in range(len(th)):
                k = (j + 1) % len(th)
                p0 = (x, 0.0, 0.0)
                p1 = (x, r * c[j], r * s[j]); p2 = (x, r * c[k], r * s[k])
                tris.append([p0, p1, p2] if sgn > 0 else [p0, p2, p1])
    return np.array(tris, dtype=float)


def prism_96gon(azimuths, radius, xs):
    """A capped polygon prism: the synthesised `fluid_env`.

    Returned as THREE NAMED SOLIDS -- inlet cap, outlet cap, lateral wall --
    so that section 3.2's inlet and outlet planes become named patches of the
    built mesh rather than being inherited from a background box."""
    np = _np()
    th = np.asarray(azimuths, dtype=float)
    c, s = np.cos(th), np.sin(th)
    wall, inlet, outlet = [], [], []
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        for j in range(len(th)):
            k = (j + 1) % len(th)
            a = (x0, radius * c[j], radius * s[j]); b = (x0, radius * c[k], radius * s[k])
            d = (x1, radius * c[j], radius * s[j]); e = (x1, radius * c[k], radius * s[k])
            wall.append([a, e, d]); wall.append([a, b, e])       # OUTWARD
    for j in range(len(th)):
        k = (j + 1) % len(th)
        x = xs[0]
        inlet.append([(x, 0.0, 0.0), (x, radius * c[k], radius * s[k]),
                      (x, radius * c[j], radius * s[j])])
        x = xs[-1]
        outlet.append([(x, 0.0, 0.0), (x, radius * c[j], radius * s[j]),
                       (x, radius * c[k], radius * s[k])])
    return {"env_wall": np.array(wall), "env_inlet": np.array(inlet),
            "env_outlet": np.array(outlet)}


def write_ascii_stl(path, solids):
    """Named-solid ASCII STL.  snappyHexMesh keys its `regions` off these names."""
    np = _np()
    with open(path, "w") as fh:
        for name, t in solids:
            fh.write("solid %s\n" % name)
            nv = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
            L = np.linalg.norm(nv, axis=1)
            L[L == 0.0] = 1.0
            nv = nv / L[:, None]
            for tri, nrm in zip(t, nv):
                fh.write("  facet normal %.10e %.10e %.10e\n    outer loop\n" % tuple(nrm))
                for v in tri:
                    fh.write("      vertex %.10e %.10e %.10e\n" % tuple(v))
                fh.write("    endloop\n  endfacet\n")
            fh.write("endsolid %s\n" % name)


def gon_radius_at(theta, circumradius, step, az0=0.0):
    """Boundary radius of a regular polygon of revolution at azimuth `theta`.

    `az0` is the azimuth of a MEASURED VERTEX and the phase is taken from it.
    THE FIRST DRAFT OF THIS FUNCTION WAS PHASE-SHIFTED BY HALF A FACET: it read
    `((theta + half) % step) - half`, which returns the FLAT radius
    (R cos 1.875 deg) at a VERTEX and the circumradius at a flat midpoint --
    exactly inverted.  The error is 0.046 % of R, invisible in a volume and
    decisive in a clearance: it reported the strut-to-core gap as 0.2679 mm
    where section 21.12 registers 0.2521 mm, and the three struts sit at
    0 deg / +-120 deg, which section 21.12 records are VERTICES of both 96-gons.
    A phase convention is not a detail when the features of interest sit on the
    vertices."""
    half = step / 2.0
    ph = ((theta - az0) % step) - half
    return circumradius * math.cos(half) / math.cos(ph)


def inside_gon_body(pts, prof, azimuths, step):
    """Point-in-body for a polygon of revolution, EXACTLY (no ray casting).

    A point is inside when its radius is below both the meridional profile at
    its x AND the polygon's boundary radius at its azimuth.  Used for the
    Monte-Carlo volume control and for every seed-point check."""
    np = _np()
    P = np.asarray(prof, dtype=float)
    p = np.atleast_2d(np.asarray(pts, dtype=float))
    x, r = p[:, 0], np.hypot(p[:, 1], p[:, 2])
    th = np.arctan2(p[:, 2], p[:, 1])
    rp = np.interp(x, P[:, 0], P[:, 1], left=-1.0, right=-1.0)
    half = step / 2.0
    ph = ((th - float(np.asarray(azimuths).ravel()[0])) % step) - half
    fac = math.cos(half) / np.cos(ph)
    return (rp >= 0.0) & (r <= rp * fac)


# ---------------------------------------------------------------------------
# THE BACKGROUND GRID.
#
# THE ONE DESIGN DECISION IN THIS SECTION, STATED OPENLY BECAUSE A LATER READER
# WILL OTHERWISE READ IT AS A DOMAIN CHANGE.  The background `blockMesh` box is
# NOT section 3.2's domain and is deliberately LARGER than it.  section 3.2's
# inlet and outlet planes are delivered by the SYNTHESISED `fluid_env` caps
# (section 21.12 registers `fluid_env.stl` as a capped prism running x_in to
# x_out); every cell outside it is removed by snappyHexMesh, so the built
# domain is section 3.2's and the box is only scaffolding.
#
# WHY IT MATTERS, and it is not cosmetic.  `G-MESHSIM` (section 14.3) reads
# Delta_0 from `constant/polyMesh/level0Edge`, and OpenFOAM computes that as the
# MINIMUM level-0 edge -- hexRef8.C, verbatim: "Note minimum so if cells are
# not cubic we use the smallest edge side."  A box pinned to section 3.2's
# 1.075000 m length cannot be divided into an integer number of 18.000 mm
# cells (1.075/0.018 = 59.72), so its cells would be NON-CUBIC and
# `level0Edge` would report the short edge -- a Delta_0 that is NOT the one the
# registration registers.  A box aligned to the lowest common multiple of the
# three registered Delta_0 values divides EXACTLY at all three levels, so the
# built `level0Edge` is 0.018 / 0.012 / 0.008 m to the digit and the gate reads
# the registered number rather than a near miss.  NO REGISTERED QUANTITY MOVES;
# the scaffolding is chosen to deliver them, which is the opposite.
# ---------------------------------------------------------------------------

def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def background_box(surface_bbox, x_in, x_out, ladder):
    """The BLOCK-aligned scaffolding box, DERIVED -- never a constant.

    Returns (lo, hi, block_um, clearance_m).  REFUSES if the three registered
    Delta_0 values have no common integral block, because then no single box
    divides exactly at every level and `level0Edge` would be a near miss at at
    least one of them.  (section 3.4's superseded 8.000 / 5.333 / 3.556 mm
    ladder is exactly such a set -- this check would have refused it.)"""
    um = []
    for lv in sorted(ladder):
        v = ladder[lv]["delta0_mm"] * 1000.0
        if abs(v - round(v)) > 1e-6:
            raise Refused("Delta_0 for %s is %.6f mm, not a whole micrometre; "
                          "no exact background division exists"
                          % (lv, ladder[lv]["delta0_mm"]))
        um.append(int(round(v)))
    block = um[0]
    for v in um[1:]:
        block = block * v // _gcd(block, v)
    # A LADDER WHOSE LEVELS SHARE NO SMALL BLOCK IS NOT BUILDABLE AS ONE BOX.
    # The registered 18 / 12 / 8 mm share 72000 um = 4 x the coarsest cell.
    # section 3.4's SUPERSEDED 8.000 / 5.333 / 3.556 mm share a block METRES
    # wide (5333 is prime), so the "aligned" box would dwarf the domain and the
    # scaffolding would dominate castellation.  Ten times the coarsest cell is
    # the bound: one block of overshoot per face is tolerable, a hundred is not.
    if block > 10 * max(um):
        raise Refused("the registered Delta_0 values %s um share no block "
                      "smaller than %d um (%.1f x the coarsest cell). No single "
                      "background box divides exactly at every level, so at "
                      "least one level's `level0Edge` would be a near miss and "
                      "G-MESHSIM would read a Delta_0 the registration does "
                      "NOT register." % (um, block, float(block) / max(um)))
    clearance = min(um) / 1.0e6                       # one FINEST base cell
    lo_req = [min(x_in, surface_bbox[0][0]) - clearance,
              surface_bbox[0][1] - clearance, surface_bbox[0][2] - clearance]
    hi_req = [max(x_out, surface_bbox[1][0]) + clearance,
              surface_bbox[1][1] + clearance, surface_bbox[1][2] + clearance]
    b = block / 1.0e6
    lo = [math.floor(v / b) * b for v in lo_req]
    hi = [math.ceil(v / b) * b for v in hi_req]
    lo = [round(v, 9) for v in lo]
    hi = [round(v, 9) for v in hi]
    for i in range(3):
        if not (lo[i] < lo_req[i] + 1e-12 and hi[i] > hi_req[i] - 1e-12):
            raise Refused("the aligned box does not contain the required "
                          "extent on axis %d" % i)
    return lo, hi, block, clearance


def divisions(lo, hi, delta0_mm):
    """Background divisions, EXACT or REFUSED.  Never rounded to fit."""
    d = delta0_mm / 1000.0
    out = []
    for i in range(3):
        n = (hi[i] - lo[i]) / d
        if abs(n - round(n)) > 1e-7:
            raise Refused("box extent %.6f m on axis %d is not an integer "
                          "number of %.3f mm cells (%.6f). A rounded division "
                          "makes the cells non-cubic, and hexRef8 then reports "
                          "the SHORT edge as level0Edge -- G-MESHSIM would read "
                          "a Delta_0 the registration does not register."
                          % (hi[i] - lo[i], i, delta0_mm, n))
        out.append(int(round(n)))
    return out


# ---------------------------------------------------------------------------
# THE DICTIONARIES.  Every registered number in them is read at write time.
# ---------------------------------------------------------------------------

_FOAM_HDR = ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
             "    class       dictionary;\n    object      %s;\n}\n")


def write_block_mesh_dict(path, lo, hi, nx):
    v = [(lo[0], lo[1], lo[2]), (hi[0], lo[1], lo[2]), (hi[0], hi[1], lo[2]),
         (lo[0], hi[1], lo[2]), (lo[0], lo[1], hi[2]), (hi[0], lo[1], hi[2]),
         (hi[0], hi[1], hi[2]), (lo[0], hi[1], hi[2])]
    with open(path, "w") as fh:
        fh.write(_FOAM_HDR % "blockMeshDict")
        fh.write("scale 1;\nvertices (\n")
        for p in v:
            fh.write("    (%.9g %.9g %.9g)\n" % p)
        fh.write(");\nblocks ( hex (0 1 2 3 4 5 6 7) (%d %d %d) "
                 "simpleGrading (1 1 1) );\n" % tuple(nx))
        # The scaffolding faces carry NO cells after snappy removes everything
        # outside `fluid_env`; they are named so a stray survivor is visible in
        # `constant/polyMesh/boundary` rather than silently merged into a
        # defaultFaces patch.
        fh.write("edges ();\nboundary ( bgBox { type wall; faces ("
                 "(0 4 7 3) (1 2 6 5) (0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)"
                 "); } );\nmergePatchPairs ();\n")


def write_sfe_dict(path, surfaces, included_angle):
    with open(path, "w") as fh:
        fh.write(_FOAM_HDR % "surfaceFeatureExtractDict")
        for s in surfaces:
            fh.write("%s { extractionMethod extractFromSurface; "
                     "extractFromSurfaceCoeffs { includedAngle %g; } "
                     "writeObj no; }\n" % (s, included_angle))


def write_snappy_dict(path, level, lev, layers, d1, seeds, regions,
                      layer_block, feature_level, resolve_feature_angle,
                      n_cells_between_levels, seed_order=None):
    """The multi-region dict.  ONE GEOMETRY ENTRY PER CLOSED BODY.

    THE DISTINCTION THE TOPOLOGY PROBE PAID FOR, stated so it is not undone:
    a `regions{}` sub-dict is fine for PATCH NAMING and is NOT fine for
    CELLZONE ASSIGNMENT.  "Inside surface X" is ONE volume; it cannot resolve to
    three different cellZones, and a geometry entry holding five disconnected
    bodies cannot be inside-tested at all.  `fluid_env` therefore keeps its
    three regions -- they only name inlet / outlet / wall patches -- while its
    cellZone sits at the TOP level; every other zone-carrying surface is its own
    single-body entry.

    section 21.12's registered method is unchanged: `locationsInMesh` plus
    `refinementSurfaces` with `cellZone` / `faceZone` / `cellZoneInside inside`.
    What changed is how the surfaces are PRESENTED to it."""
    zone = {"duct": "duct", "hub": "housing", "strutA": "housing",
            "strutB": "housing", "strutC": "housing", "core": "core"}
    slev = {"duct": lev["duct"], "hub": lev["hub"], "core": lev["hub"],
            "strutA": lev["strut"], "strutB": lev["strut"], "strutC": lev["strut"]}
    # `core` IS LISTED FIRST BECAUSE IT IS NESTED INSIDE `hub` AND THE INSIDE-
    # TEST PRECEDENCE IS FIRST-WINS.  That precedence is MEASURED, not assumed:
    # probe D of 2026-09-11 listed `hub`->housing before `core`->core and
    # `core` came out at ZERO CELLS in all three seed orders, with housing
    # holding the core's volume.  Innermost first is the rule this produces.
    bodies = ("core", "duct", "hub", "strutA", "strutB", "strutC")
    with open(path, "w") as fh:
        w = fh.write
        w(_FOAM_HDR % "snappyHexMeshDict")
        w("castellatedMesh true;\nsnap true;\naddLayers true;\n\ngeometry\n{\n")
        for nm in bodies:
            w("    %s.stl { type triSurfaceMesh; name %s; }\n" % (nm, nm))
        w("    fluid_env.stl { type triSurfaceMesh; name env;\n"
          "        regions { env_wall {name env_wall;} env_inlet {name inlet;} "
          "env_outlet {name outlet;} } }\n}\n\n")
        w("castellatedMeshControls\n{\n")
        w("    maxLocalCells 8000000;\n    maxGlobalCells 30000000;\n"
          "    minRefinementCells 10;\n    nCellsBetweenLevels %d;\n"
          % n_cells_between_levels)
        w("    features (\n")
        for nm in bodies:
            w('        { file "%s.eMesh"; level %d; }\n' % (nm, slev[nm]))
        w('        { file "fluid_env.eMesh"; level %d; }\n' % lev["duct"])
        w("    );\n")
        w("    refinementSurfaces\n    {\n")
        for nm in bodies:
            w("        %-7s { level (%d %d); faceZone %s_fz; faceType internal; "
              "cellZone %s; cellZoneInside inside; patchInfo { type wall; } }\n"
              % (nm, slev[nm], slev[nm], nm, zone[nm]))
        w("        env     { level (%d %d); faceZone env_fz; cellZone fluid; "
          "cellZoneInside inside;\n            regions\n            {\n"
          % (lev["duct"], lev["duct"]))
        for rn, pt in (("env_wall", "wall"), ("inlet", "patch"), ("outlet", "patch")):
            w("                %-8s { level (%d %d); patchInfo { type %s; } }\n"
              % (rn, lev["duct"], lev["duct"], pt))
        w("            } }\n    }\n")
        w("    resolveFeatureAngle %g;\n    refinementRegions {}\n"
          % resolve_feature_angle)
        w("    locationsInMesh\n    (\n")
        for rg in (seed_order or regions):
            p_ = seeds[rg]
            w("        ((%.9g %.9g %.9g) %s)\n" % (p_[0], p_[1], p_[2], rg))
        w("    );\n    allowFreeStandingZoneFaces true;\n}\n\n")
        w("snapControls { nSmoothPatch 5; tolerance 1.0; nSolveIter 100; "
          "nRelaxIter 8; nFeatureSnapIter 15; implicitFeatureSnap false; "
          "explicitFeatureSnap true; multiRegionFeatureSnap true; }\n\n")
        w(layer_block)
        w("\nmeshQualityControls { maxNonOrtho 65; maxBoundarySkewness 20; "
          "maxInternalSkewness 4; maxConcave 80; minVol 1e-13; "
          "minTetQuality 1e-9; minArea -1; minTwist 0.02; minDeterminant 0.001; "
          "minFaceWeight 0.02; minVolRatio 0.01; minTriangleTwist -1; "
          "nSmoothScale 4; errorReduction 0.75; }\nmergeTolerance 1e-6;\n")


def layer_controls(layers, d1):
    """The addLayersControls block, on the registered counts and Delta_1.

    `relativeSizes false` and the FIRST_AND_EXPANSION pair are the supervisor's
    approved 2026-09-11 form; the NUMBERS are read from the registration."""
    per = []
    for nm, key in (("hub", "hub"), ("strutA", "strut"), ("strutB", "strut"),
                    ("strutC", "strut")):
        per.append("    %-7s { nSurfaceLayers %2d; firstLayerThickness %.6g; }"
                   % (nm, layers[key], d1["wall"]))
    per.append("    %-7s { nSurfaceLayers %2d; firstLayerThickness %.6g; }"
               % ("duct", layers["duct"], d1["duct"]))
    return ("addLayersControls\n{\n"
            "  relativeSizes false;\n"
            "  firstLayerThickness %.6g;\n  expansionRatio 1.2;\n"
            "  layers\n  {\n%s\n  }\n"
            "  minThickness 2.0e-5;\n  maxFaceThicknessRatio 0.5;\n"
            "  maxThicknessToMedialRatio 0.3;\n"
            "  nGrow 0; featureAngle 60; nRelaxIter 5;\n"
            "  nSmoothSurfaceNormals 1; nSmoothNormals 3; nSmoothThickness 10;\n"
            "  minMedialAxisAngle 90; nBufferCellsNoExtrude 0; nLayerIter 50;\n}\n"
            % (d1["wall"], "\n".join(per)))


def write_control_dict(path, end_time):
    """The case's OWN controlDict -- `analyse_t26.case_end_time()` reads
    endTime from HERE (mark_done_t26.py:169), so the value is written from the
    registered ladder and this file holds no copy of it."""
    with open(path, "w") as fh:
        fh.write(_FOAM_HDR % "controlDict")
        fh.write("application chtMultiRegionSimpleFoam;\nstartFrom startTime;\n"
                 "startTime 0;\nstopAt endTime;\nendTime %d;\ndeltaT 1;\n"
                 "writeControl timeStep;\nwriteInterval %d;\nwriteFormat ascii;\n"
                 "writePrecision 8;\nrunTimeModifiable true;\n"
                 % (int(end_time), int(end_time)))
        fh.write("// meshing-phase stub: blockMesh/snappyHexMesh need a "
                 "controlDict, and this one already carries the REGISTERED "
                 "endTime so the value is never written twice.\n")


def write_fv_stubs(system_dir):
    with open(os.path.join(system_dir, "fvSchemes"), "w") as fh:
        fh.write(_FOAM_HDR % "fvSchemes")
        fh.write("ddtSchemes{default steadyState;}\ngradSchemes{default Gauss linear;}\n"
                 "divSchemes{default none;}\nlaplacianSchemes{default Gauss linear corrected;}\n"
                 "interpolationSchemes{default linear;}\nsnGradSchemes{default corrected;}\n")
    with open(os.path.join(system_dir, "fvSolution"), "w") as fh:
        fh.write(_FOAM_HDR % "fvSolution")
        fh.write("solvers{}\n")


# ---------------------------------------------------------------------------
# THE DETACHED DRIVER.
#
# TWO T26 MESHES HAVE ALREADY BEEN LOST to a foreground build being SIGTERMed
# when its agent session died.  The driver is GENERATED into the mesh
# directory (so it needs no instrument pin) and:
#   * re-executes itself under `setsid`, reparented to init;
#   * CAPTURES rc INSIDE THE CHILD, never around the setsid line -- `setsid
#     timeout cmd` exits 0 for every outcome, so an rc taken outside is the
#     `setsid parent returns zero` trap wearing a detachment hat;
#   * REFUSES if the mesh directory already exists, so a restart can never
#     half-overwrite a tree somebody is reading;
#   * traps TERM/INT/HUP and records WHICH signal, so "died again" is
#     distinguishable from "still meshing";
#   * writes a HEARTBEAT every HEARTBEAT_PERIOD_S = 30 seconds carrying pid,
#     PPID, phase, elapsed seconds and polyMesh byte count.  THIRTY SECONDS IS
#     THE DOCUMENTED PERIOD: a snappy phase that writes nothing for two
#     consecutive beats is stalled, not slow.
# ---------------------------------------------------------------------------

HEARTBEAT_PERIOD_S = 30
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"   # launch_t26.sh:222

_DRIVER = r'''#!/usr/bin/env bash
# GENERATED by build_t26.py --mesh.  NOT a repository instrument: it carries no
# registered quantity of its own -- every number in it was written here by the
# generator, which read them from the registration.
set -u
D="__MESHDIR__"; FOAM="__FOAM__"; LV="__LEVEL__"; HB=__HB__
SELF=$(readlink -f "$0")
if [ "${T26_MESH_DETACHED:-0}" != "1" ]; then
  rm -f "$D/mesh.pid" "$D/launch.out"
  setsid env T26_MESH_DETACHED=1 bash "$SELF" >"$D/launch.out" 2>&1 </dev/null &
  i=0; while [ $i -lt 20 ]; do [ -s "$D/mesh.pid" ] && break; sleep 1; i=$((i+1)); done
  CPID=$(cat "$D/mesh.pid" 2>/dev/null || true)
  case "$CPID" in ''|*[!0-9]*)
    echo "MESH LAUNCH FAILED: no child pid after ${i}s; see $D/launch.out" >&2; exit 92 ;;
  esac
  if ! kill -0 "$CPID" 2>/dev/null; then
    if [ -s "$D/MESH_RC.txt" ]; then
      echo "MESH $LV DETACHED child_pid=$CPID ALREADY_FINISHED rc=$(cat "$D/MESH_RC.txt")"; exit 0
    fi
    echo "MESH LAUNCH FAILED: child $CPID neither alive nor finished" >&2; exit 93
  fi
  echo "MESH $LV DETACHED child_pid=$CPID state=$D/BUILD_STATE.txt heartbeat=$D/HEARTBEAT.txt period_s=$HB"
  exit 0
fi
echo $$ > "$D/mesh.pid"
T0=$(date +%s)
phase(){ printf '%s %s elapsed_s=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$1" \
  "$(( $(date +%s) - T0 ))" >> "$D/BUILD_STATE.txt"; printf '%s\n' "$1" > "$D/PHASE.txt"; }
on_exit(){ _rc=$?; printf '%s SHELL_EXIT rc=%s last_phase=%s elapsed_s=%s\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$_rc" "$(cat "$D/PHASE.txt" 2>/dev/null)" \
  "$(( $(date +%s) - T0 ))" >> "$D/BUILD_STATE.txt"; }
trap on_exit EXIT
trap 'phase KILLED_SIGTERM; exit 143' TERM
trap 'phase KILLED_SIGINT;  exit 130' INT
trap 'phase KILLED_SIGHUP;  exit 129' HUP
phase "START pid=$$ ppid=$PPID level=$LV"
cd "$D" || exit 90
set +u; . "$FOAM" >/dev/null 2>&1 || true; set -u
( while kill -0 $$ 2>/dev/null; do
    printf '%s pid=%s ppid=%s phase=%s elapsed_s=%s polyMesh_bytes=%s\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$$" "$(ps -o ppid= -p $$ 2>/dev/null | tr -d ' ')" \
      "$(cat "$D/PHASE.txt" 2>/dev/null)" "$(( $(date +%s) - T0 ))" \
      "$(du -sb "$D/constant" 2>/dev/null | cut -f1)" > "$D/HEARTBEAT.txt"
    sleep $HB
  done ) & HBPID=$!
t0=$(date +%s)
phase blockMesh
timeout 1800  blockMesh                       > log.blockMesh 2>&1; rcb=$?
phase "surfaceFeatureExtract blockMesh_rc=$rcb"
timeout 900   surfaceFeatureExtract           > log.sfe       2>&1; rcf=$?
phase "snappyHexMesh sfe_rc=$rcf"
timeout 28800 snappyHexMesh -overwrite        > log.snappy    2>&1; rcs=$?
phase "splitMeshRegions snappy_rc=$rcs"
[ -f "$D/constant/polyMesh/level0Edge" ] && cp "$D/constant/polyMesh/level0Edge" "$D/LEVEL0EDGE.preserved"
timeout 7200  splitMeshRegions -cellZones -overwrite > log.split 2>&1; rcp=$?
# G-MESHSIM (section 14.3) reads `constant/polyMesh/level0Edge`.
# splitMeshRegions moves the mesh into constant/<region>/polyMesh, so that file
# -- the one the REGISTERED READER names -- can cease to exist.  It is
# preserved here, unmodified, before the split can remove it.  ABSENT IS NEVER
# A PASSING VALUE for that reader, so this is the difference between a graded
# ladder and three NOT A RESULT rows.
if [ -f "$D/LEVEL0EDGE.preserved" ] && [ ! -f "$D/constant/polyMesh/level0Edge" ]; then
  mkdir -p "$D/constant/polyMesh" && cp "$D/LEVEL0EDGE.preserved" "$D/constant/polyMesh/level0Edge"
fi
t1=$(date +%s)
phase "checkMesh split_rc=$rcp"
# section 13.7: the FULL check set, with the command line recorded INTO the log.
CM="checkMesh -allRegions -allGeometry -allTopology"
echo "CHECKMESH COMMAND LINE: $CM" > log.checkMesh
timeout 7200 $CM >> log.checkMesh 2>&1; rcc=$?
t2=$(date +%s)
printf 'level=%s blockMesh_rc=%s sfe_rc=%s snappy_rc=%s split_rc=%s checkMesh_rc=%s mesh_wall_s=%s total_wall_s=%s\n' \
  "$LV" "$rcb" "$rcf" "$rcs" "$rcp" "$rcc" "$((t1-t0))" "$((t2-t0))" > "$D/MESH_RC.txt"
kill $HBPID 2>/dev/null
if [ "$rcb" = 0 ] && [ "$rcf" = 0 ] && [ "$rcs" = 0 ] && [ "$rcp" = 0 ]; then
  phase "FINISHED $(cat "$D/MESH_RC.txt")"; echo ok > "$D/MESH_DONE.txt"; exit 0
fi
phase "FAILED $(cat "$D/MESH_RC.txt")"; exit 1
'''


def write_driver(mesh_dir, level, foam_bashrc=None):
    p = os.path.join(mesh_dir, "run_mesh.sh")
    txt = (_DRIVER.replace("__MESHDIR__", mesh_dir).replace("__LEVEL__", level)
           .replace("__FOAM__", foam_bashrc or FOAM_BASHRC)
           .replace("__HB__", str(HEARTBEAT_PERIOD_S)))
    with open(p, "w") as fh:
        fh.write(txt)
    os.chmod(p, 0o755)
    return p


# ---------------------------------------------------------------------------
# THE REGION-SPLIT CONTROL (binding condition 2).
# ---------------------------------------------------------------------------

def built_regions(mesh_dir):
    """The regions ACTUALLY on disk: a `constant/<name>/polyMesh/owner` each."""
    const = os.path.join(mesh_dir, "constant")
    if not os.path.isdir(const):
        return []
    out = []
    for name in sorted(os.listdir(const)):
        if name == "polyMesh":
            continue
        if os.path.isfile(os.path.join(const, name, "polyMesh", "owner")):
            out.append(name)
    return out


def check_regions(mesh_dir, registered=None):
    """REFUSE unless the built region set IS the registered region set.

    A build that silently delivers three regions where four are registered is
    the failure this exists to stop: three regions still solve, still converge
    and still produce a number, and the missing conjugate path is invisible in
    every downstream artifact.  The expected set is READ from section 3.1, so
    this check cannot drift from the registration it enforces."""
    want = list(registered if registered is not None else reg_regions())
    got = built_regions(mesh_dir)
    if sorted(got) != sorted(want):
        missing = [r for r in want if r not in got]
        extra = [r for r in got if r not in want]
        raise Refused(
            "REGION SPLIT REFUSED: the build produced %d region(s) %s where "
            "section 3.1 registers %d %s%s%s. A level whose region set is not "
            "the registered one is NOT a level; it is not graded around."
            % (len(got), sorted(got), len(want), sorted(want),
               ("; MISSING %s" % missing) if missing else "",
               ("; UNREGISTERED %s" % extra) if extra else ""))
    # THE CONNECTIVITY GATE.  A registered region that exists and is internally
    # disconnected is not a region: no conduction crosses a fragment boundary,
    # and the count above cannot see it.
    disc = read_region_disconnect(os.path.join(mesh_dir, "log.checkMesh"))
    if disc:
        broken = dict((k, v) for k, v in disc.items() if k in want and v > 1)
        if broken:
            raise Refused(
                "REGION(S) INTERNALLY DISCONNECTED: %s (region -> number of "
                "face-disconnected components, from `checkMesh -allRegions`). "
                "A region in fragments carries no conduction between them, and "
                "a region-COUNT check passes it. section 3.1 registers "
                "`housing` and `duct` as a conjugate path; fragments are not a "
                "path." % broken)
    return got


# ---------------------------------------------------------------------------
# LOG READERS.  Each returns None on absence and is driven in BOTH directions.
# ---------------------------------------------------------------------------

def read_cell_counts(mesh_dir):
    """Per-region cell counts, from each region's own `polyMesh/owner` header."""
    out = {}
    for rg in built_regions(mesh_dir):
        p = os.path.join(mesh_dir, "constant", rg, "polyMesh", "owner")
        try:
            head = open(p, "r", errors="replace").read(4096)
        except (IOError, OSError):
            continue
        m = re.search(r"nCells:\s*([0-9]+)", head)
        if m:
            out[rg] = int(m.group(1))
    return out


def read_checkmesh_summary(path):
    """The checkMesh summary AND the recorded command line (section 13.7).

    REFUSES a log whose recorded command line lacks -allGeometry or
    -allTopology: bare `checkMesh` prints `Mesh OK.` on a mesh that fails
    checks which only run under those flags."""
    if not os.path.isfile(path):
        return None
    txt = open(path, "r", errors="replace").read()
    m = re.search(r"^CHECKMESH COMMAND LINE:\s*(.+)$", txt, re.M)
    if not m:
        raise Refused("%s records no command line; section 13.7 requires the "
                      "artifact to prove which instrument produced it" % path)
    cmd = m.group(1).strip()
    missing = [f for f in ("-allGeometry", "-allTopology") if f not in cmd]
    if missing:
        raise Refused("%s was produced by `%s`, which lacks %s. Bare checkMesh "
                      "prints `Mesh OK.` on a mesh that fails the checks those "
                      "flags enable (section 13.7)." % (path, cmd, missing))
    return {
        "command_line": cmd,
        "failed_checks": len(re.findall(r"\*\*\*", txt)),
        "mesh_ok": bool(re.search(r"^\s*Mesh OK\.", txt, re.M)),
        "geometric_directions": (
            int(re.search(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions", txt).group(1))
            if re.search(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions", txt) else None),
    }


def read_closed_named_surfaces(path):
    """snappyHexMesh's OWN count of usable closed named surfaces.

    Reads back the line "Found N closed, named surfaces."  A build in which N
    is short of the number of zone-carrying surfaces has SILENTLY fallen back
    to the seed walk for the remainder -- which is the defect the topology
    probe found, and OpenFOAM announced it in plain text while the build
    returned rc = 0."""
    if not os.path.isfile(path):
        return None
    m = re.findall(r"Found (\d+) closed, named surfaces",
                   open(path, "r", errors="replace").read())
    return int(m[-1]) if m else 0


def read_region_disconnect(path):
    """Per-region disconnected-component count, from `checkMesh -allRegions`.

    A REGION-COUNT CHECK CANNOT SEE THIS.  The probe produced a `duct` region
    that EXISTED and was 206 fragments; counting region directories returns
    four and passes.  checkMesh prints "Number of regions: N" per region and
    that N is the thing to gate."""
    if not os.path.isfile(path):
        return None
    txt = open(path, "r", errors="replace").read()
    out, cur = {}, None
    for line in txt.splitlines():
        m = re.search(r"Create mesh for region\s+(\S+)", line)
        if m:
            cur = m.group(1)
            out.setdefault(cur, 1)
            continue
        m = re.search(r"Number of regions:\s*(\d+)", line)
        if m and cur:
            out[cur] = int(m.group(1))
    return out


def read_layer_coverage(path):
    """Achieved layer coverage per patch, from snappyHexMesh's own table."""
    if not os.path.isfile(path):
        return None
    txt = open(path, "r", errors="replace").read()
    blocks = re.findall(r"^patch\s+faces\s+layers\s+overall thickness.*?\n"
                        r"(?:.*?\n)?((?:\s*\S+\s+\d+\s+[0-9.]+\s+.*\n)+)", txt, re.M)
    if not blocks:
        return {}
    out = {}
    for line in blocks[-1].strip().splitlines():
        f = line.split()
        if len(f) >= 3:
            try:
                out[f[0]] = {"faces": int(f[1]), "layers": float(f[2])}
            except ValueError:
                continue
    return out


#: THREE GENERIC RAY DIRECTIONS, NO ZERO COMPONENT.  The first draft used
#: (-0.3, 0.9539, 0.0): a direction with dz = 0 travels inside a constant-z
#: plane, and every lateral facet of a polygon-of-revolution is an AXIAL strip,
#: so such a ray grazes edges by construction.  The disagreement check below
#: caught it on the duct.  Directions here are mutually non-coplanar with the
#: geometry's own planes and share no rational relationship with the 3.75 deg
#: facet pitch.
_RAY_DIRS = ((0.5773502692, 0.5257311121, 0.6234898019),
             (-0.4472135955, 0.7071067812, 0.5477225575),
             (0.3826834324, -0.6087614290, 0.6946583705))


def ray_inside(tris, pts, dirs=_RAY_DIRS):
    """Point-in-closed-surface by parity, with THREE independent rays REQUIRED
    TO AGREE UNANIMOUSLY.  A single ray that grazes an edge miscounts by one
    and SILENTLY INVERTS the answer; directions disagreeing is a REFUSAL, never
    a vote -- a majority of three would hide exactly the case worth seeing."""
    np = _np()
    P = np.atleast_2d(np.asarray(pts, dtype=float))
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    e1, e2 = v1 - v0, v2 - v0
    res = []
    for d in dirs:
        d = np.asarray(d, dtype=float)
        d = d / np.linalg.norm(d)
        h = np.cross(d, e2)
        a = np.einsum("ij,ij->i", e1, h)
        par = np.abs(a) < 1e-12
        inv = np.where(par, 0.0, 1.0 / np.where(par, 1.0, a))
        hits = []
        for p in P:
            s = p - v0
            u = np.einsum("ij,ij->i", s, h) * inv
            q = np.cross(s, e1)
            vv = (q @ d) * inv
            t = np.einsum("ij,ij->i", e2, q) * inv
            ok = (~par) & (u >= 0) & (u <= 1) & (vv >= 0) & (u + vv <= 1) & (t > 1e-12)
            hits.append(int(ok.sum()) % 2 == 1)
        res.append(np.array(hits))
    for i in range(1, len(res)):
        if not np.array_equal(res[0], res[i]):
            bad = [j for j in range(len(res[0])) if res[0][j] != res[i][j]]
            raise Refused("the inside-tests DISAGREE for point index %s -- ray "
                          "0 says %s, ray %d says %s. A ray grazed an edge; the "
                          "answer is REFUSED, not voted on."
                          % (bad, [bool(res[0][j]) for j in bad], i,
                             [bool(res[i][j]) for j in bad]))
    return res[0]


# ---------------------------------------------------------------------------
# THE BIRTH CERTIFICATE (section 3.6, binding condition 1).
#
# "One per level ... carrying: the STL sha256, the snappyHexMeshDict /
#  blockMeshDict sha256, every registered level parameter of section 3.4, the
#  checkMesh summary, the measured cell count, the achieved layer coverage per
#  patch, and the sha256 of the certificate's own inputs.  A LEVEL WITH NO
#  CERTIFICATE IS NOT A LEVEL AND CANNOT BE GRADED."
#
# THE CERTIFICATE IS READ, AND THE READ IS WHAT MAKES IT EVIDENCE.  `certify()`
# writes it and IMMEDIATELY reads it back through `read_certificate()`, so the
# production path drives the reader on every real build.  A certificate that
# nothing reads is the same defect as a freeze that verifies bytes and never
# call sites, one layer on.
# ---------------------------------------------------------------------------

CERT_SCHEMA = "T26_MESH_BIRTH_CERTIFICATE"
CERT_VERSION = 1
CERT_REQUIRED = ("schema", "version", "level", "written_utc", "registration",
                 "surface", "dicts", "synthesised_surfaces",
                 "registered_level_parameters", "background", "built",
                 "checkMesh", "layer_coverage", "closed_named_surfaces",
                 "region_components", "inputs_sha256")


def _inputs_digest(doc):
    import hashlib
    body = dict((k, v) for k, v in doc.items() if k != "inputs_sha256")
    return hashlib.sha256(json.dumps(body, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def read_certificate(path, level=None, registration=None):
    """THE READER.  Returns the certificate, or REFUSES.  Never degrades.

    Refusal arms, every one driven in mesh_selftest() against a live positive:
      absent | unparseable | wrong schema/version | a required key missing |
      inputs digest mismatch (a hand-edited certificate) | surface sha not the
      registered one | level mismatch | a registered level parameter that
      disagrees with the LIVE registration | a built region set that is not the
      registered one."""
    if not os.path.isfile(path):
        raise Refused("NO BIRTH CERTIFICATE at %s. section 3.6: 'A level with "
                      "no certificate is not a level and cannot be graded.'" % path)
    try:
        doc = json.loads(open(path, "r", errors="replace").read())
    except ValueError as exc:
        raise Refused("the birth certificate at %s does not parse as JSON (%s). "
                      "A malformed certificate is refused, never repaired."
                      % (path, exc))
    if not isinstance(doc, dict):
        raise Refused("the birth certificate at %s is not a JSON object" % path)
    if doc.get("schema") != CERT_SCHEMA or doc.get("version") != CERT_VERSION:
        raise Refused("the certificate at %s declares schema %r version %r; this "
                      "reader accepts %r version %r only"
                      % (path, doc.get("schema"), doc.get("version"),
                         CERT_SCHEMA, CERT_VERSION))
    missing = [k for k in CERT_REQUIRED if k not in doc]
    if missing:
        raise Refused("the certificate at %s is INCOMPLETE -- section 3.6 "
                      "requires %s, and these are absent: %s"
                      % (path, list(CERT_REQUIRED), missing))
    if _inputs_digest(doc) != doc["inputs_sha256"]:
        raise Refused("the certificate at %s does not match its own "
                      "`inputs_sha256`. It has been edited since it was "
                      "written, so nothing in it is evidence of the build it "
                      "claims to certify." % path)
    if level is not None and doc["level"] != level:
        raise Refused("the certificate at %s certifies level %s, not %s"
                      % (path, doc["level"], level))
    text = _reg_text(registration)
    want_sha = reg_stl_sha256(text)
    got_sha = (doc.get("surface") or {}).get("sha256")
    if got_sha != want_sha:
        raise Refused("the certificate at %s was built on surface sha256 %s; "
                      "the registration pins %s. section 21.12: 'A file "
                      "identical in every respect we checked is still not the "
                      "file the registration pins.'"
                      % (path, got_sha, want_sha))
    ladder = read_registered_ladder(registration or REGISTRATION)[doc["level"]]
    rp = doc["registered_level_parameters"]
    for key in ("delta0_mm", "endTime", "ranks", "cells_projected"):
        src = {"cells_projected": "cells"}.get(key, key)
        if key not in rp:
            raise Refused("the certificate at %s records no %r" % (path, key))
        if float(rp[key]) != float(ladder[src]):
            raise Refused("the certificate at %s records %s = %s; the "
                          "REGISTERED-LADDER line for %s registers %s. A "
                          "certificate that disagrees with its registration "
                          "certifies nothing."
                          % (path, key, rp[key], doc["level"], ladder[src]))
    want_regions = sorted(reg_regions(text))
    got_regions = sorted((doc.get("built") or {}).get("regions") or [])
    if got_regions != want_regions:
        raise Refused("the certificate at %s certifies regions %s; section 3.1 "
                      "registers %s" % (path, got_regions, want_regions))
    return doc


def certificate_path(level, repo_root=None):
    rel, name = reg_certificate_path()
    root = repo_root or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
    return os.path.join(root, rel.rstrip("/"), level, name)


def certify(level, mesh_dir, out_path=None, registration=None, repo_root=None):
    """Write the birth certificate for a BUILT level, then READ IT BACK.

    REFUSES before writing if the built region set is not the registered one,
    and refuses after writing if the reader will not accept what was written."""
    text = _reg_text(registration)
    ladder = read_registered_ladder(registration or REGISTRATION)[level]
    lev = reg_surface_levels(text)[level]
    regions = check_regions(mesh_dir, reg_regions(text))
    counts = read_cell_counts(mesh_dir)
    l0 = os.path.join(mesh_dir, "constant", "polyMesh", "level0Edge")
    l0v = None
    if os.path.isfile(l0):
        m = re.search(r"value\s+([-+0-9.eE]+)\s*;", open(l0, errors="replace").read())
        if m:
            l0v = float(m.group(1))
    plan = json.loads(open(os.path.join(mesh_dir, "MESH_PLAN.json"),
                           errors="replace").read())
    if plan.get("throwaway_levels"):
        raise Refused("this mesh was built with THROWAWAY surface levels (%s) "
                      "and no birth certificate may be written from it. "
                      "section 3.6's certificate carries 'every registered "
                      "level parameter'; a level the registration does not "
                      "register is not one." % plan["throwaway_levels"])
    doc = {
        "schema": CERT_SCHEMA, "version": CERT_VERSION, "level": level,
        "written_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "registration": {"path": os.path.relpath(registration or REGISTRATION),
                         "sha256": sha256_of(registration or REGISTRATION)},
        "surface": plan["surface"],
        "dicts": dict((n, sha256_of(os.path.join(mesh_dir, "system", n)))
                      for n in ("blockMeshDict", "snappyHexMeshDict",
                                "surfaceFeatureExtractDict")
                      if os.path.isfile(os.path.join(mesh_dir, "system", n))),
        "synthesised_surfaces": dict(
            (n, sha256_of(os.path.join(mesh_dir, "constant", "triSurface", n)))
            for n in ("core.stl", "fluid_env.stl")
            if os.path.isfile(os.path.join(mesh_dir, "constant", "triSurface", n))),
        "registered_level_parameters": {
            "delta0_mm": ladder["delta0_mm"], "endTime": ladder["endTime"],
            "ranks": ladder["ranks"], "cells_projected": ladder["cells"],
            "surface_levels": lev, "layers": reg_layers(text),
            "delta1_m": reg_delta1(text)},
        "background": plan["background"],
        "built": {"regions": regions, "cells_per_region": counts,
                  "cells_total": sum(counts.values()) if counts else 0,
                  "level0Edge_m": l0v, "mesh_root": mesh_dir,
                  "rc_line": (open(os.path.join(mesh_dir, "MESH_RC.txt"),
                                   errors="replace").read().strip()
                              if os.path.isfile(os.path.join(mesh_dir, "MESH_RC.txt"))
                              else None)},
        "checkMesh": read_checkmesh_summary(os.path.join(mesh_dir, "log.checkMesh")),
        "closed_named_surfaces": read_closed_named_surfaces(
            os.path.join(mesh_dir, "log.snappy")),
        "region_components": read_region_disconnect(
            os.path.join(mesh_dir, "log.checkMesh")),
        "layer_coverage": read_layer_coverage(os.path.join(mesh_dir, "log.snappy")),
    }
    doc["inputs_sha256"] = _inputs_digest(doc)
    path = out_path or certificate_path(level, repo_root)
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with open(path, "w") as fh:
        fh.write(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    read_certificate(path, level=level, registration=registration)   # DRIVEN
    return path, doc


# ---------------------------------------------------------------------------
# THE BUILD.
# ---------------------------------------------------------------------------

def build_surfaces(stl_path, out_dir, registration=None, verbose=True):
    """Synthesise `core.stl` and `fluid_env.stl` FROM THE REGISTERED BINARY STL.

    Returns a dict of measurements.  Every synthesis step carries its own
    control and REFUSES rather than emitting a surface it cannot vouch for."""
    np = _np()
    text = _reg_text(registration)
    say = (lambda s: print(s)) if verbose else (lambda s: None)

    want_sha = reg_stl_sha256(text)
    got_sha = sha256_of(stl_path)
    if got_sha != want_sha:
        raise Refused("%s is sha256 %s; the registration pins %s. section 21.12 "
                      "names a byte-different ASCII copy of this very surface "
                      "whose vertex set matches to 1e-6 m: 'A file identical in "
                      "every respect we checked is still not the file the "
                      "registration pins.'" % (stl_path, got_sha, want_sha))
    say("  surface sha256 %s -- MATCHES the registered pin" % got_sha[:16])

    tris = read_binary_stl(stl_path)
    comps = split_components(tris, reg_component_measurements(text))
    say("  index split reproduces section 21.12 on all five components "
        "(volumes and areas), so file order is CHECKED, not trusted")

    prof, spread = hub_profile(comps["hub"]["tris"])
    hub_az, step = gon_azimuths(comps["hub"]["tris"],
                                max(r for _, r in prof))
    gon_step = step
    say("  hub is a %d-gon of revolution, station radius spread %.2e m, "
        "vertex pitch %.6f deg" % (len(hub_az), spread, math.degrees(step)))

    inset = reg_core_inset(text)
    # THE INSET IS APPLIED TO THE FACETED SURFACE, NOT TO AN IDEALISED SURFACE
    # OF REVOLUTION.  The hub on disk is a 96-gon prism-of-revolution, and every
    # flat face lies at the APOTHEM R cos(1.875 deg), not at R.  A 4 mm erosion
    # moves each face plane inward by 4 mm, so the offset is taken in the
    # apothem coordinate and converted back afterwards.
    #
    # IT IS A 2.2 MICROMETRE DIFFERENCE AND IT MATTERS.  Eroding the idealised
    # surface instead gives a core circumradius of 0.0335000 at the barrel and a
    # strut-to-core clearance of 0.2500 mm; eroding the FACETS gives 0.0334978
    # and 0.2522 mm -- which is section 21.12's registered 0.2521 mm.  The
    # difference is 0.006 % of a radius and it is the difference between
    # reproducing the registration and not.  The facets are what
    # snappyHexMesh meshes, so the faceted erosion is the physical one.
    cosh_ = math.cos(gon_step / 2.0)
    apo = [(x, r * cosh_) for x, r in prof]
    core_apo = miter_offset_profile(apo, inset)
    core_prof = [[x, r / cosh_] for x, r in core_apo]
    core_tris = revolve(core_prof, hub_az)
    core_vol = signed_volume(core_tris)
    if core_vol <= 0:
        raise Refused("the synthesised core has signed volume %+.6e -- its "
                      "normals point inward and GEO-4's condition fails" % core_vol)
    # CONTROL: an independent volume by Monte Carlo on the same profile.
    rng = np.random.RandomState(20260911)
    lo = core_tris.reshape(-1, 3).min(0)
    hi = core_tris.reshape(-1, 3).max(0)
    N = 2000000
    pts = lo + rng.rand(N, 3) * (hi - lo)
    frac = float(inside_gon_body(pts, core_prof, hub_az, step).mean())
    mc = frac * float(np.prod(hi - lo))
    se = float(np.prod(hi - lo)) * math.sqrt(max(frac * (1 - frac), 0.0) / N)
    if abs(mc - core_vol) > max(6.0 * se, 2.0e-3 * abs(core_vol)):
        raise Refused("the synthesised core's two independent volumes DISAGREE: "
                      "revolve %.6e m3 vs Monte Carlo %.6e +- %.1e m3. A 4 mm "
                      "inset that two methods do not agree on is not the "
                      "registered `core`." % (core_vol, mc, se))
    say("  core: revolve %.6e m3, Monte Carlo %.6e +- %.1e m3 (agree %.3f %%); "
        "axial span [%.7f, %.7f]"
        % (core_vol, mc, se, 100.0 * abs(mc - core_vol) / core_vol,
           core_prof[0][0], core_prof[-1][0]))

    # THE CLEARANCE THAT MAKES THE ZONE ASSIGNMENT ORDER-INDEPENDENT.
    # section 21.12: "Minimum strut -> core clearance: 0.2521 mm ... `core` and
    # `strut` are therefore disjoint sets, no cell centre can lie in both, and
    # the `core`-versus-`housing` cellZone assignment is ORDER-INDEPENDENT.
    # REGISTERED AS A BUILD ASSERT, not as a reassurance."
    # SAMPLED OVER THE STRUT SURFACE, NOT ITS VERTICES.  A vertex-only minimum
    # is an UPPER bound: the closest approach of a convex box to a convex body
    # of revolution can fall in a FACE interior with every corner further away.
    # section 21.12 registers 0.2521 mm; a vertex-only reader returns 0.2679 mm
    # and would have reported a clearance the surface does not have.
    _st = np.vstack([comps[k]["tris"] for k in ("strutA", "strutB", "strutC")])
    _bc = np.array([(i / 8.0, j / 8.0, 1.0 - i / 8.0 - j / 8.0)
                    for i in range(9) for j in range(9 - i)])
    sp = np.einsum("bk,fkd->bfd", _bc, _st).reshape(-1, 3)
    cp = np.asarray(core_prof, dtype=float)
    rr = np.hypot(sp[:, 1], sp[:, 2])
    th = np.arctan2(sp[:, 2], sp[:, 1])
    rprof = np.interp(sp[:, 0], cp[:, 0], cp[:, 1], left=-1.0, right=-1.0)
    half = step / 2.0
    ph = ((th - hub_az[0]) % step) - half
    rcore = np.where(rprof < 0, -1.0, rprof * math.cos(half) / np.cos(ph))
    gap = float(np.min(np.where(rcore < 0, 1.0, rr - rcore)))
    if gap <= 0.0:
        raise Refused("A STRUT POINT LIES INSIDE THE CORE (clearance %.6f mm). "
                      "section 21.12 registers `core` and `strut` DISJOINT; if "
                      "they are not, the cellZone assignment is ORDER-DEPENDENT "
                      "and the mesh changes when nothing changed." % (gap * 1e3))
    say("  strut -> core minimum clearance %.4f mm > 0: `core` and `strut` are "
        "DISJOINT, so the cellZone assignment is ORDER-INDEPENDENT" % (gap * 1e3))

    # fluid_env: the phase is MEASURED off the duct bore, never assumed.
    bore_r = float(np.hypot(comps["duct"]["tris"][:, :, 1],
                            comps["duct"]["tris"][:, :, 2]).min())
    duct_az, duct_step = gon_azimuths(comps["duct"]["tris"], bore_r)
    if len(duct_az) != len(hub_az) or abs(duct_step - step) > 1e-9:
        raise Refused("the duct bore is a %d-gon of pitch %.9f rad and the hub "
                      "is a %d-gon of pitch %.9f rad; section 21.12 registers "
                      "that they share ONE phase"
                      % (len(duct_az), duct_step, len(hub_az), step))
    dphi = max(abs(((a - b + math.pi) % (2 * math.pi)) - math.pi)
               for a, b in zip(sorted(duct_az), sorted(hub_az)))
    if dphi > 1e-6:
        raise Refused("the duct bore and the hub do NOT share a phase "
                      "(max vertex azimuth difference %.3e rad)" % dphi)
    x_in, x_out = reg_domain_x(text)
    duct_x0 = float(comps["duct"]["tris"][:, :, 0].min())
    duct_x1 = float(comps["duct"]["tris"][:, :, 0].max())
    rings = sorted(set([x_in, duct_x0, duct_x1, x_out]))
    env = prism_96gon(duct_az, bore_r, rings)
    env_all = np.vstack([env[k] for k in ("env_wall", "env_inlet", "env_outlet")])
    env_vol = signed_volume(env_all)
    if env_vol <= 0:
        raise Refused("the synthesised fluid_env has signed volume %+.6e" % env_vol)
    say("  fluid_env: %d-gon prism, circumradius %.6f (MEASURED off the duct "
        "bore), x %.6f -> %.6f, rings at %s, volume %.6e m3"
        % (len(duct_az), bore_r, x_in, x_out,
           ["%.4f" % v for v in rings], env_vol))

    os.makedirs(out_dir, exist_ok=True)
    import shutil as _sh
    _sh.copyfile(stl_path, os.path.join(out_dir, "motor_in_duct.stl"))
    write_ascii_stl(os.path.join(out_dir, "core.stl"), [("core", core_tris)])
    write_ascii_stl(os.path.join(out_dir, "fluid_env.stl"),
                    [(k, env[k]) for k in ("env_wall", "env_inlet", "env_outlet")])
    # ONE FILE PER CLOSED BODY -- the repair the topology probe forced.  Each
    # zone-carrying surface is its own `triSurfaceMesh` with its cellZone at the
    # TOP level, so every one of them is a single closed body that
    # `cellZoneInside inside` can actually test.  Bundling them cost this rung
    # a mesh in which `duct` held 86 % of the cells.
    for nm in ("hub", "duct", "strutA", "strutB", "strutC"):
        write_ascii_stl(os.path.join(out_dir, "%s.stl" % nm), [(nm, comps[nm]["tris"])])

    # THE CONTROL, DRIVEN ON EVERY BUILD: each zone-carrying surface is ONE part.
    bodies = {"core.stl": core_tris, "fluid_env.stl": env_all}
    for nm in ("hub", "duct", "strutA", "strutB", "strutC"):
        bodies["%s.stl" % nm] = comps[nm]["tris"]
    multi = []
    for fn, tt in sorted(bodies.items()):
        k = surface_parts(tt)
        if k != 1:
            multi.append("%s has %d disconnected parts" % (fn, k))
    if multi:
        raise Refused(
            "A ZONE-CARRYING SURFACE IS NOT A SINGLE CLOSED BODY: %s. "
            "`cellZoneInside inside` needs a searchable volume; a multi-part "
            "entry is not one, snappyHexMesh silently falls back to the seed "
            "walk, and the walk leaks through any surface too coarse to seal. "
            "MEASURED 2026-09-11: with five bodies in one entry, snappy found "
            "2 closed named surfaces out of 3 supplied, `duct` took 172,001 of "
            "199,684 cells, and splitMeshRegions returned 206 unnamed domains."
            % "; ".join(multi))
    say("  every zone-carrying surface is ONE closed body (%d checked): "
        "cellZoneInside has a searchable volume for each" % len(bodies))

    return dict(sha256=got_sha, registered_sha256=want_sha, path=stl_path,
                components=dict((k, dict(facets=len(v["tris"]), vol=v["vol"],
                                         area=v["area"], bbox=v["bbox"]))
                                for k, v in comps.items()),
                hub_profile=prof, core_profile=[list(p) for p in core_prof],
                azimuths=duct_az, gon_step_rad=step, bore_circumradius=bore_r,
                core_volume_revolve=core_vol, core_volume_mc=mc, core_volume_mc_se=se,
                core_inset_m=inset, strut_core_clearance_m=gap,
                env_volume=env_vol, env_rings=rings, domain_x=[x_in, x_out],
                bbox=[tris.reshape(-1, 3).min(0).tolist(),
                      tris.reshape(-1, 3).max(0).tolist()],
                comps_obj=comps, core_tris_obj=core_tris,
                env_tris_obj=env_all)


def derive_seeds(surf, regions, verbose=True):
    """One `locationsInMesh` seed per REGISTERED region, DERIVED and CHECKED.

    Each seed is tested against every component: it must be inside its own
    region and OUTSIDE all the others.  A seed in the wrong region silently
    hands snappy a different decomposition from the registered one -- and the
    build would still succeed."""
    np = _np()
    say = (lambda s: print(s)) if verbose else (lambda s: None)
    comps = surf["comps_obj"]
    prof = surf["hub_profile"]
    cprof = surf["core_profile"]
    az, step = surf["azimuths"], surf["gon_step_rad"]
    x_in, x_out = surf["domain_x"]
    hub_x0 = min(x for x, _ in prof)
    duct_x0, duct_x1 = (comps["duct"]["bbox"][0][0], comps["duct"]["bbox"][1][0])
    strut_x0 = comps["strutA"]["bbox"][0][0]
    bore = surf["bore_circumradius"]
    duct_out = float(np.hypot(comps["duct"]["tris"][:, :, 1],
                              comps["duct"]["tris"][:, :, 2]).max())
    # a FLAT-midpoint azimuth: the furthest an angle can be from any vertex,
    # so a seed is never within snapping distance of a polygon edge.
    flat = az[0] + step / 2.0
    cmax = max(r for _, r in cprof)
    xcore = [x for x, r in cprof if abs(r - cmax) < 1e-9][0]
    seeds = {
        "fluid":   (0.5 * (x_in + hub_x0), 0.0, 0.0),
        "core":    (xcore, 0.0, 0.0),
        "housing": (xcore, 0.5 * (cmax + max(r for _, r in prof)) * math.cos(flat),
                    0.5 * (cmax + max(r for _, r in prof)) * math.sin(flat)),
        "duct":    (0.5 * (duct_x0 + strut_x0),
                    0.5 * (bore + duct_out) * math.cos(flat),
                    0.5 * (bore + duct_out) * math.sin(flat)),
    }
    missing = [r for r in regions if r not in seeds]
    if missing:
        raise Refused("no seed point is derivable for registered region(s) %s; "
                      "snappyHexMesh keeps only what a locationsInMesh entry "
                      "reaches, so an unseeded region is a region that will not "
                      "exist" % missing)
    P = [seeds[r] for r in regions]

    # ------------------------------------------------------------------
    # THE MESHING ENVELOPE.  Binding condition from the supervisor after the
    # topology probe: a seed outside the envelope REFUSES, loudly, at build
    # time.  The probe's `duct` seed sat at r = 0.127500 while `fluid_env` is a
    # prism at circumradius 0.125000, and derive_seeds passed it because it
    # only ever asked "is this seed inside the body it names".
    #
    # THE ENVELOPE IS THE UNION OF THE REGISTERED REGIONS, NOT `fluid_env`.
    # Stated because the narrow reading is tempting and wrong: the duct solid
    # legitimately lies OUTSIDE `fluid_env` -- section 21.12 registers
    # `fluid_env` at 0.125000 as the fluid/duct INTERFACE, and an interface is
    # not a bound on the mesh.  Checking seeds against `fluid_env` would refuse
    # a correct `duct` seed.  What is refused here is a seed outside EVERY
    # registered region, which is a seed in the scaffolding.
    if surf.get("env_tris_obj") is not None:
        in_env = (ray_inside(surf["env_tris_obj"], P)
                  | ray_inside(comps["duct"]["tris"], P))
        stray = [regions[i] for i in range(len(P)) if not in_env[i]]
        if stray:
            raise Refused(
                "SEED(S) OUTSIDE THE MESHING ENVELOPE: %s. A seed in the "
                "scaffolding names a region that snappyHexMesh will grow "
                "through the whole background box. MEASURED 2026-09-11: the "
                "probe's `duct` zone took 172,001 of 199,684 cells and "
                "splitMeshRegions returned 206 unnamed domains." % stray)
        say("    every seed lies inside the envelope (fluid_env u duct), which "
            "is the UNION of the registered regions and not `fluid_env` alone")

    in_hub = inside_gon_body(P, prof, az, step)
    in_core = inside_gon_body(P, cprof, az, step)
    in_duct = ray_inside(comps["duct"]["tris"], P)
    in_strut = np.zeros(len(P), dtype=bool)
    for k in ("strutA", "strutB", "strutC"):
        in_strut = in_strut | ray_inside(comps[k]["tris"], P)
    want = {"fluid": (False, False, False, False), "core": (True, True, False, False),
            "housing": (True, False, False, False), "duct": (False, False, True, False)}
    bad = []
    for i, r in enumerate(regions):
        got = (bool(in_hub[i]), bool(in_core[i]), bool(in_duct[i]), bool(in_strut[i]))
        if r in want and got != want[r]:
            bad.append("%s seed %s: (hub,core,duct,strut) = %s, expected %s"
                       % (r, ["%.6f" % v for v in seeds[r]], got, want[r]))
        say("    seed %-8s %-34s hub=%d core=%d duct=%d strut=%d"
            % (r, "(%.6f %.6f %.6f)" % seeds[r], got[0], got[1], got[2], got[3]))
    if bad:
        raise Refused("SEED POINTS ARE IN THE WRONG REGIONS: " + "; ".join(bad))
    return seeds


#: Dictionary settings that are NOT registered per level.  section 3.3 registers
#: `resolveFeatureAngle 30` and `nCellsBetweenLevels 3` in prose; the included
#: angle is discussed in the report that accompanies this instrument.
RESOLVE_FEATURE_ANGLE = 30.0
N_CELLS_BETWEEN_LEVELS = 3
INCLUDED_ANGLE = 150.0   # section 3.3 registers 30; MEASURED to extract ZERO edges
                         # on this surface (L1ABS/log.sfe: "points : 0, edges : 0").
                         # surfaceFeatures.C:199 sets minCos = cos(180 - angle),
                         # so 30 selects only normals differing by MORE than 150
                         # deg and a 90 deg strut box edge (n.n = 0) is not one.
                         # RULED by the heat-transfer supervisor 2026-09-11;
                         # travels to the same addendum as the two controls below.


def mesh(level, go=False, mesh_root=None, registration=None, stl=None,
         foam_bashrc=None, verbose=True, seed_order=None,
         throwaway_levels=None, expect_cells=None):
    """Stage and (optionally) LAUNCH the mesh build for one registered level.

    WITHOUT --go nothing is executed: the surfaces are synthesised, every
    control is driven, the dictionaries are written and the plan is printed.
    That is deliberate -- the object every gate measures is produced here, so
    the staged case is reviewable before a single core-minute is spent."""
    say = (lambda s: print(s)) if verbose else (lambda s: None)
    text = _reg_text(registration)
    ladder = read_registered_ladder(registration or REGISTRATION)
    if level not in ladder:
        raise Refused("%r is not a registered level; the REGISTERED-LADDER "
                      "lines carry %s" % (level, sorted(ladder)))
    row = ladder[level]
    lev = dict(reg_surface_levels(text)[level])
    if throwaway_levels:
        # A THROWAWAY OVERRIDE, AND IT REGISTERS NOTHING.  It exists so a
        # hypothesis about the REGISTERED levels can be tested without
        # registering a replacement for them.  Three fences, all driven:
        #   * it REFUSES to touch the registered mesh root;
        #   * the deviation is stamped into MESH_PLAN.json, so it cannot be
        #     mistaken later for a registered build;
        #   * `certify()` REFUSES outright on a plan carrying it, so no birth
        #     certificate can ever be written from an overridden level.
        if mesh_root is None or reg_mesh_root(text).rstrip("/") in \
                os.path.abspath(mesh_root).rstrip("/"):
            raise Refused("--throwaway-levels may not be used under the "
                          "REGISTERED mesh root %s. A level the registration "
                          "does not register never writes where graded meshes "
                          "live." % reg_mesh_root(text))
        for kv in throwaway_levels.split(","):
            k, _, v = kv.partition("=")
            if k.strip() not in lev:
                raise Refused("--throwaway-levels names %r, which is not one of "
                              "the registered surfaces %s" % (k, sorted(lev)))
            lev[k.strip()] = int(v)
        say("  *** THROWAWAY LEVEL OVERRIDE: %s -- REGISTERS NOTHING, and no "
            "birth certificate can be written from this build ***" % lev)
    layers, d1 = reg_layers(text), reg_delta1(text)
    regions = reg_regions(text)
    root = mesh_root or reg_mesh_root(text)
    mdir = os.path.join(root.rstrip("/"), level)
    stl = stl or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))),
                              "cases", "demo-surfaces", "motor_in_duct.stl")

    say("T26 MESH BUILD -- level %s" % level)
    say("  REGISTERED (read, not held): Delta_0 %.3f mm | endTime %d | ranks %d "
        "| projected cells %d" % (row["delta0_mm"], row["endTime"], row["ranks"],
                                  row["cells"]))
    say("  REGISTERED surface levels: duct %d (%.4f mm), hub %d (%.4f mm), "
        "strut %d (%.4f mm)"
        % (lev["duct"], row["delta0_mm"] / 2 ** lev["duct"],
           lev["hub"], row["delta0_mm"] / 2 ** lev["hub"],
           lev["strut"], row["delta0_mm"] / 2 ** lev["strut"]))
    say("  REGISTERED regions (section 3.1): %s" % regions)

    if os.path.exists(mdir):
        raise Refused("%s already exists. This builder never writes into an "
                      "existing mesh tree: a half-overwritten polyMesh is "
                      "indistinguishable from a finished one, and somebody may "
                      "be reading it." % mdir)

    st = os.statvfs(os.path.dirname(root.rstrip("/")) or "/")
    free_gb = st.f_bavail * st.f_frsize / 1024.0 ** 3
    # THE GUARD READS THE LEVELS ACTUALLY IN USE, NOT THE REGISTERED ONES.
    # It used to price `row["cells"]` unconditionally, so under a throwaway
    # override it printed "0.89 GiB (402,409 cells)" while the build produced
    # ~1.07 M -- an instrument holding a registered value where a read belongs,
    # which is the defect class this rung has now produced eight times. Seven
    # were repaired; this is the eighth and it is repaired here rather than
    # left standing as a disclosure, because a log that reads authoritatively
    # is worse than one that reads uncertainly.
    # THE GUARD READS THE LEVELS ACTUALLY IN USE, AND WHEN IT CANNOT DERIVE A
    # COUNT IT REFUSES TO INVENT ONE.
    #
    # It used to price `row["cells"]` unconditionally, so under a throwaway
    # override it printed "0.89 GiB (402,409 cells)" while the build produced
    # ~1.07 M -- an instrument holding a registered value where a read belongs.
    #
    # THE FIRST REPAIR WAS WORSE THAN THE DEFECT AND IS RECORDED RATHER THAN
    # QUIETLY REPLACED: scaling the registered count by 4^(level rise) on the
    # most-raised surface gave a 16x bump and a 14.16 GiB "bound" against a
    # true build of ~1.07 M cells = 2.35 GiB. That guard would have REFUSED the
    # very launch that exposed the defect, at 13.2 GiB free. A fabricated
    # bound that blocks correct work is not a safer guard, it is a louder one.
    #
    # So: with an override in force the cell count is genuinely unknown to this
    # instrument, and the caller must STATE it. No number is invented, and no
    # correct build is refused by a number nobody measured.
    if throwaway_levels and not expect_cells:
        raise Refused(
            "--throwaway-levels changes the surface levels, so the registered "
            "cell count %d no longer describes this build and this instrument "
            "will not price it from a value it knows to be wrong. Pass "
            "--expect-cells N with a stated basis. (Refusing to invent the "
            "number is the point: the previous repair invented a 16x bound "
            "that would have refused a build needing 2.35 GiB at 13.2 GiB "
            "free.)" % row["cells"])
    cells_est = int(expect_cells) if expect_cells else row["cells"]
    est_gb = cells_est * 2.2e-6         # ~2.2 kB/cell, measured on the ABS family
    say("  DISK: %.1f GiB free at %s; %.2f GiB for %d cells at 2.2 kB/cell "
        "(the rate measured on the mesh-development family)%s"
        % (free_gb, root, est_gb, cells_est,
           " -- count STATED by the caller, not registered" if expect_cells else ""))

    tri = os.path.join(mdir, "constant", "triSurface")
    sysd = os.path.join(mdir, "system")
    os.makedirs(tri)
    os.makedirs(sysd)
    surf = build_surfaces(stl, tri, registration, verbose=verbose)
    say("  SEEDS (one per registered region, each checked against every "
        "component):")
    seeds = derive_seeds(surf, regions, verbose=verbose)

    lo, hi, block, clear = background_box(surf["bbox"], surf["domain_x"][0],
                                          surf["domain_x"][1], ladder)
    nx = divisions(lo, hi, row["delta0_mm"])
    say("  BACKGROUND BOX (scaffolding, NOT section 3.2's domain): "
        "(%.3f %.3f %.3f) -> (%.3f %.3f %.3f), block %d um, clearance %.3f mm"
        % (lo[0], lo[1], lo[2], hi[0], hi[1], hi[2], block, clear * 1e3))
    say("  DIVISIONS %d x %d x %d -> cells EXACTLY %.6f mm cubic, so "
        "level0Edge == the registered Delta_0 (hexRef8 reports the MINIMUM "
        "level-0 edge)" % (nx[0], nx[1], nx[2], row["delta0_mm"]))

    write_block_mesh_dict(os.path.join(sysd, "blockMeshDict"), lo, hi, nx)
    write_sfe_dict(os.path.join(sysd, "surfaceFeatureExtractDict"),
                   ("duct.stl", "hub.stl", "strutA.stl", "strutB.stl",
                    "strutC.stl", "core.stl", "fluid_env.stl"), INCLUDED_ANGLE)
    write_snappy_dict(os.path.join(sysd, "snappyHexMeshDict"), level, lev,
                      layers, d1, seeds, regions,
                      layer_controls(layers, d1), None,
                      RESOLVE_FEATURE_ANGLE, N_CELLS_BETWEEN_LEVELS,
                      seed_order=seed_order)
    write_control_dict(os.path.join(sysd, "controlDict"), row["endTime"])
    write_fv_stubs(sysd)

    plan = {
        "level": level, "mesh_dir": mdir,
        "surface": {"path": surf["path"], "sha256": surf["sha256"],
                    "registered_sha256": surf["registered_sha256"]},
        "background": {"box_lo": lo, "box_hi": hi, "divisions": nx,
                       "block_um": block, "clearance_m": clear,
                       "delta0_mm": row["delta0_mm"]},
        "seeds": dict((k, list(v)) for k, v in seeds.items()),
        "seed_order": list(seed_order or regions),
        "throwaway_levels": throwaway_levels,
        "expect_cells": int(expect_cells) if expect_cells else None,
        "surface_levels_used": lev,
        "surface_measurements": dict(
            (k, surf[k]) for k in ("core_volume_revolve", "core_volume_mc",
                                   "core_volume_mc_se", "core_inset_m",
                                   "strut_core_clearance_m", "env_volume",
                                   "env_rings", "domain_x", "bore_circumradius",
                                   "gon_step_rad")),
    }
    with open(os.path.join(mdir, "MESH_PLAN.json"), "w") as fh:
        fh.write(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    drv = write_driver(mdir, level, foam_bashrc)
    say("  STAGED: %s" % mdir)
    say("  driver: %s (detached; rc captured INSIDE the child; heartbeat every "
        "%d s)" % (drv, HEARTBEAT_PERIOD_S))
    if not go:
        say("  NOT LAUNCHED -- pass --go to execute. The mesh is the object "
            "every gate measures, so the staged case is reviewable first.")
        return mdir, plan
    rc = subprocess.call(["bash", drv])
    if rc != 0:
        raise Refused("the mesh driver refused to launch (rc %d); see %s"
                      % (rc, os.path.join(mdir, "launch.out")))
    pidf = os.path.join(mdir, "mesh.pid")
    deadline = time.time() + 120.0
    pid = ppid = None
    while time.time() < deadline:
        try:
            pid = int(open(pidf).read().strip())
            ppid = int(open("/proc/%d/stat" % pid).read().split(") ", 1)[1].split()[1])
        except (IOError, OSError, ValueError, IndexError):
            ppid = None
        if ppid == 1:
            break
        if ppid is None and os.path.isfile(os.path.join(mdir, "MESH_RC.txt")):
            break
        time.sleep(2)
    say("  LAUNCHED pid=%s ppid=%s (PPID 1 confirms reparenting to init: the "
        "build outlives this agent)" % (pid, ppid))
    if ppid != 1 and not os.path.isfile(os.path.join(mdir, "MESH_RC.txt")):
        raise Refused("the mesh child did not reparent to init within 120 s "
                      "(pid %s, ppid %s). An attached build dies with its "
                      "session -- two T26 meshes have already been lost that "
                      "way." % (pid, ppid))
    return mdir, plan



# ===========================================================================
# THE PLANTED CONTROLS FOR THE MESH INSTRUMENT (`CLAUDE.md` rule 3).
#
# EVERY REFUSAL ARM BELOW IS DRIVEN AGAINST A LIVE POSITIVE ARM.  A reader that
# has only ever been shown refusing has not been shown able to accept, and a
# refusal it cannot avoid is not evidence of anything -- it is the planted-zero
# defect with the sign flipped.  So each block runs the CLEAN case first,
# requires it to PASS, and only then mutates one thing and requires the SAME
# production function to refuse.
# ===========================================================================

def _arm(label, fn, must_refuse, fails, needle=None, verbose=True):
    err = None
    try:
        fn()
    except Refused as exc:
        err = str(exc)
    except Exception as exc:                        # noqa: BLE001 - reported, not hidden
        err = "NON-REFUSAL EXCEPTION %s: %s" % (type(exc).__name__, exc)
        fails.append(label + " (crashed)")
        if verbose:
            print("  [BAD] %s -- %s" % (label, err[:160]))
        return
    ok = (err is not None) == must_refuse
    if ok and must_refuse and needle and needle.lower() not in err.lower():
        ok = False
    if not ok:
        fails.append(label)
    if verbose:
        tail = (" -> %s" % err.split(".")[0][:120]) if err else ""
        print("  [%s] %s%s" % ("ok " if ok else "BAD", label, tail))


def _float_control():
    """Refuse with whatever `float()` raises on the registration's own minus
    sign.  If float() ever stops raising, this control goes red and says so."""
    try:
        v = float("\u22120.175000")
    except ValueError as exc:
        raise Refused("float() raised: %s" % exc)
    raise Refused("float() did NOT raise; it returned %r, so the U+2212 trap "
                  "this control exists to demonstrate no longer exists" % v)


def mesh_selftest(verbose=True):
    """Drive every control of the mesh instrument.  No OpenFOAM, no solver."""
    import shutil as _sh
    import tempfile
    say = (lambda s: print(s)) if verbose else (lambda s: None)
    fails = []
    say("build_t26.py MESH INSTRUMENT -- planted controls")
    say("=" * 74)
    tmp = tempfile.mkdtemp(prefix="t26_mesh_selftest_")
    try:
        text = _reg_text()
        reg_copy = os.path.join(tmp, "REG.md")

        # ---- 1. THE REGISTRATION READERS, POSITIVE ARM FIRST --------------
        say("-- registration readers: the registered values, READ --")
        ladder = read_registered_ladder(REGISTRATION)
        lev = reg_surface_levels(text)
        say("   ladder      %s" % dict((k, (v["delta0_mm"], v["endTime"], v["ranks"]))
                                       for k, v in sorted(ladder.items())))
        say("   surf levels %s" % dict(sorted(lev.items())))
        say("   layers      %s   Delta_1 %s" % (reg_layers(text), reg_delta1(text)))
        say("   regions     %s" % reg_regions(text))
        say("   domain x    %s   core inset %.4f m" % (list(reg_domain_x(text)),
                                                       reg_core_inset(text)))
        say("   mesh root   %s" % reg_mesh_root(text))
        say("   cert path   %s<level>/%s" % reg_certificate_path(text))
        _arm("CONTROL: all registration readers parse the REAL registration",
             lambda: [reg_stl_sha256(text), reg_regions(text), reg_domain_x(text),
                      reg_core_inset(text), reg_surface_levels(text),
                      reg_layers(text), reg_delta1(text), reg_mesh_root(text),
                      reg_certificate_path(text), reg_component_measurements(text)],
             False, fails, verbose=verbose)

        def _doctor(sub, rep, count=1):
            open(reg_copy, "w").write(text.replace(sub, rep, count))
            return reg_copy

        _arm("MUTATION: section 3.1's region table removed -> REFUSE",
             lambda: reg_regions(open(_doctor("### 3.1 Regions", "### 3.1 Gone"),
                                      errors="replace").read()),
             True, fails, "3.1", verbose=verbose)
        _arm("MUTATION: section 21.4 says strut level 4 but prints 2.2500 mm "
             "-> REFUSE (registration disagrees with itself)",
             lambda: reg_surface_levels(open(_doctor("**4 (1.1250 mm)**",
                                                     "**4 (2.2500 mm)**"),
                                             errors="replace").read()),
             True, fails, "internally inconsistent", verbose=verbose)
        _arm("MUTATION: the inlet plane moved DOWNSTREAM of the outlet -> REFUSE",
             lambda: reg_domain_x(open(_doctor("x = **\u22120.175000 m**",
                                               "x = **+0.975000 m**"),
                                       errors="replace").read()),
             True, fails, "upstream", verbose=verbose)
        # THE UNICODE MINUS, DRIVEN IN BOTH DIRECTIONS.  section 3.2 writes the
        # inlet plane with U+2212, not ASCII '-'.  A reader that misses it
        # reads a POSITIVE inlet plane and builds a background box that does
        # not contain the domain -- and nothing downstream would say so.  The
        # naive reader must therefore FAIL on the registration's own
        # characters, and ours must not; showing only the second proves nothing.
        _arm("CONTROL: `float()` REFUSES the registration's own U+2212 string, "
             "so this trap is real and not a precaution",
             lambda: _float_control(), True, fails, "float() raised",
             verbose=verbose)
        say("   `_num()` reads that same U+2212 string as %.6f, and the clean "
            "read of section 3.2 returns inlet %.6f outlet %.6f"
            % ((_num("\u22120.175000"),) + reg_domain_x(text)))

        # ---- 2. THE BACKGROUND GRID ---------------------------------------
        say("-- background grid --")
        bbox = [[0.0, -0.13, -0.13], [0.2, 0.13, 0.13]]
        lo, hi, blk, cl = background_box(bbox, *reg_domain_x(text), ladder=ladder)
        for lv in sorted(ladder):
            nx = divisions(lo, hi, ladder[lv]["delta0_mm"])
            say("   %s Delta_0 %.3f mm -> divisions %s, cells %d, EXACTLY cubic"
                % (lv, ladder[lv]["delta0_mm"], nx, nx[0] * nx[1] * nx[2]))
        _arm("CONTROL: the registered ladder divides the aligned box exactly at "
             "every level", lambda: [divisions(lo, hi, ladder[l]["delta0_mm"])
                                     for l in ladder], False, fails, verbose=verbose)
        _arm("MUTATION: section 3.4's SUPERSEDED 8.000/5.333/3.556 mm ladder -> "
             "REFUSE (no common integral block)",
             lambda: background_box(bbox, *reg_domain_x(text), ladder={
                 "L1": {"delta0_mm": 8.0}, "L2": {"delta0_mm": 5.333},
                 "L3": {"delta0_mm": 3.556}}),
             True, fails, "no block smaller", verbose=verbose)
        _arm("MUTATION: a box extent that is not a whole number of cells -> REFUSE",
             lambda: divisions([0.0, 0.0, 0.0], [1.075, 0.288, 0.288], 18.0),
             True, fails, "integer number", verbose=verbose)

        # ---- 3. THE SURFACE -----------------------------------------------
        say("-- surface synthesis, from the REGISTERED BINARY STL --")
        stl = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))),
                           "cases", "demo-surfaces", "motor_in_duct.stl")
        surf = None
        if os.path.isfile(stl):
            out = os.path.join(tmp, "tri")
            _arm("CONTROL: core.stl and fluid_env.stl synthesise from the "
                 "REGISTERED BINARY with every control green",
                 lambda: build_surfaces(stl, os.path.join(tmp, "ctl"),
                                        verbose=False),
                 False, fails, verbose=verbose)
            surf = build_surfaces(stl, out, verbose=verbose)
            say("   seeds:")
            seeds = derive_seeds(surf, reg_regions(text), verbose=verbose)
            _arm("CONTROL: every seed lies in its own region and outside all "
                 "others", lambda: derive_seeds(surf, reg_regions(text), False),
                 False, fails, verbose=verbose)

            bad_stl = os.path.join(tmp, "mutant.stl")
            raw = bytearray(open(stl, "rb").read())
            raw[200] ^= 0x01
            open(bad_stl, "wb").write(bytes(raw))
            _arm("MUTATION: one byte of the surface flipped -> REFUSE on sha256",
                 lambda: build_surfaces(bad_stl, os.path.join(tmp, "m1"), verbose=False),
                 True, fails, "sha256", verbose=verbose)

            _arm("MUTATION: seed for `housing` moved onto the axis (into `core`) "
                 "-> REFUSE",
                 lambda: _seed_mutant(surf, text), True, fails, "wrong regions",
                 verbose=verbose)
            _arm("MUTATION: a seed pushed OUTSIDE the meshing envelope (the "
                 "probe's own failure) -> REFUSE",
                 lambda: _envelope_mutant(surf, text), True, fails,
                 "OUTSIDE THE MESHING ENVELOPE", verbose=verbose)
        else:
            fails.append("surface (STL absent at %s)" % stl)
            say("  [BAD] the registered surface is not at %s" % stl)

        # ---- 4. THE REGION-SPLIT CONTROL (binding condition 2) -------------
        say("-- the region split: four registered, four required --")
        want = reg_regions(text)
        mdir = os.path.join(tmp, "mesh")

        def _fabricate(regions, cells=1000, frag=1, closed=7):
            _sh.rmtree(mdir, ignore_errors=True)
            for r in regions:
                d = os.path.join(mdir, "constant", r, "polyMesh")
                os.makedirs(d)
                open(os.path.join(d, "owner"), "w").write(
                    "FoamFile{version 2.0;} // note: nCells: %d\n" % cells)
            os.makedirs(os.path.join(mdir, "system"), exist_ok=True)
            for n in ("blockMeshDict", "snappyHexMeshDict",
                      "surfaceFeatureExtractDict"):
                open(os.path.join(mdir, "system", n), "w").write("// %s\n" % n)
            cm = ["CHECKMESH COMMAND LINE: checkMesh -allRegions -allGeometry "
                  "-allTopology",
                  "Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)"]
            for r in regions:
                cm += ["Create mesh for region %s" % r,
                       "    Number of regions: %d" % (frag if r == "duct" else 1)]
            cm.append("Mesh OK.")
            open(os.path.join(mdir, "log.checkMesh"), "w").write("\n".join(cm) + "\n")
            open(os.path.join(mdir, "log.snappy"), "w").write(
                "Found %d closed, named surfaces. Assigning cells\nEnd\n" % closed)
            open(os.path.join(mdir, "MESH_PLAN.json"), "w").write(json.dumps({
                "surface": {"path": "cases/demo-surfaces/motor_in_duct.stl",
                            "sha256": reg_stl_sha256(text),
                            "registered_sha256": reg_stl_sha256(text)},
                "background": {"box_lo": lo, "box_hi": hi,
                               "divisions": divisions(lo, hi, ladder["L1"]["delta0_mm"]),
                               "block_um": blk}}))
            return mdir

        _fabricate(want)
        _arm("CONTROL: a tree carrying all %d registered regions is ACCEPTED"
             % len(want), lambda: check_regions(mdir, want), False, fails,
             verbose=verbose)
        _fabricate(want[:-1])
        _arm("MUTATION: THREE regions where %d are registered -> REFUSE, naming "
             "the missing one" % len(want),
             lambda: check_regions(mdir, want), True, fails, "MISSING",
             verbose=verbose)
        _fabricate(want + ["rogue"])
        _arm("MUTATION: an UNREGISTERED fifth region -> REFUSE",
             lambda: check_regions(mdir, want), True, fails, "UNREGISTERED",
             verbose=verbose)

        say("-- the connectivity gate: a region that EXISTS but is in fragments --")
        _fabricate(want, frag=1)
        _arm("CONTROL: every registered region reports ONE component -> ACCEPTED",
             lambda: check_regions(mdir, want), False, fails, verbose=verbose)
        _fabricate(want, frag=32)
        _arm("MUTATION: `duct` reports 32 disconnected components -> REFUSE "
             "(the region COUNT is still four, and still passes)",
             lambda: check_regions(mdir, want), True, fails,
             "INTERNALLY DISCONNECTED", verbose=verbose)
        _fabricate(want, frag=206)
        _arm("MUTATION: the PROBE's own 206 fragments -> REFUSE",
             lambda: check_regions(mdir, want), True, fails,
             "INTERNALLY DISCONNECTED", verbose=verbose)
        _fabricate(want, frag=1)

        say("-- snappyHexMesh's OWN closed-named-surface count, read back --")
        _arm("CONTROL: a log reporting 7 closed named surfaces reads 7",
             lambda: (_ for _ in ()).throw(Refused("x")) if
             read_closed_named_surfaces(os.path.join(mdir, "log.snappy")) != 7
             else None, False, fails, verbose=verbose)
        _fabricate(want, closed=2)
        got2 = read_closed_named_surfaces(os.path.join(mdir, "log.snappy"))
        _arm("CONTROL: the PROBE's own log line (2 of 3 supplied) reads back as "
             "%s, so the silent walk-fallback is DETECTABLE" % got2,
             lambda: None, (got2 != 2), fails, verbose=verbose)
        _fabricate(want)

        say("-- single-closed-body control on zone-carrying surfaces --")
        one = revolve([[0.0, 0.0], [0.01, 0.005], [0.02, 0.0]], [0.0, 2.094, 4.189])
        _arm("CONTROL: a single closed body counts 1 part",
             lambda: None, surface_parts(one) != 1, fails, verbose=verbose)
        two = _np().vstack([one, one + _np().array([1.0, 0.0, 0.0])])
        _arm("MUTATION: two disjoint closed bodies in ONE entry count %d parts "
             "-- the shape of the probe's `motor` file" % surface_parts(two),
             lambda: None, surface_parts(two) != 2, fails, verbose=verbose)

        # ---- 5. THE BIRTH CERTIFICATE (binding condition 1) ----------------
        say("-- the birth certificate: PRODUCED and READ --")
        _fabricate(want)
        cert = os.path.join(tmp, "MESH_BIRTH_CERTIFICATE.json")
        _arm("CONTROL: a certificate is WRITTEN for a complete build, and the "
             "writer READS IT BACK before returning",
             lambda: certify("L1", mdir, out_path=cert), False, fails,
             verbose=verbose)
        _arm("CONTROL: the reader ACCEPTS that certificate",
             lambda: read_certificate(cert, "L1"), False, fails, verbose=verbose)
        doc = json.loads(open(cert).read())
        say("   certificate carries: %s" % sorted(doc))

        def _write(d, p=None):
            open(p or cert, "w").write(json.dumps(d))

        _arm("MUTATION: NO certificate at all -> REFUSE ('a level with no "
             "certificate is not a level')",
             lambda: read_certificate(os.path.join(tmp, "absent.json"), "L1"),
             True, fails, "NO BIRTH CERTIFICATE", verbose=verbose)
        open(os.path.join(tmp, "trunc.json"), "w").write(
            json.dumps(doc)[: len(json.dumps(doc)) // 2])
        _arm("MUTATION: a truncated certificate -> REFUSE (malformed, never "
             "repaired)",
             lambda: read_certificate(os.path.join(tmp, "trunc.json"), "L1"),
             True, fails, "does not parse", verbose=verbose)
        for key in ("checkMesh", "layer_coverage", "built", "dicts"):
            d = dict(doc)
            d.pop(key)
            _write(d)
            _arm("MUTATION: required key %r deleted -> REFUSE (incomplete)" % key,
                 lambda: read_certificate(cert, "L1"), True, fails, "INCOMPLETE",
                 verbose=verbose)
        d = dict(doc)
        d["built"] = dict(d["built"])
        d["built"]["cells_total"] = 999999999
        _write(d)
        _arm("MUTATION: a value edited without re-deriving `inputs_sha256` -> "
             "REFUSE", lambda: read_certificate(cert, "L1"), True, fails,
             "inputs_sha256", verbose=verbose)
        d = dict(doc)
        d["surface"] = dict(d["surface"])
        d["surface"]["sha256"] = "5" * 64
        d["inputs_sha256"] = _inputs_digest(d)
        _write(d)
        _arm("MUTATION: built on a DIFFERENT surface (digest re-derived, so only "
             "the sha pin catches it) -> REFUSE",
             lambda: read_certificate(cert, "L1"), True, fails, "registration pins",
             verbose=verbose)
        d = dict(doc)
        d["built"] = dict(d["built"])
        d["built"]["regions"] = want[:-1]
        d["inputs_sha256"] = _inputs_digest(d)
        _write(d)
        _arm("MUTATION: a certificate claiming THREE regions -> REFUSE",
             lambda: read_certificate(cert, "L1"), True, fails, "registers",
             verbose=verbose)
        d = dict(doc)
        d["registered_level_parameters"] = dict(d["registered_level_parameters"])
        d["registered_level_parameters"]["endTime"] = 8200
        d["inputs_sha256"] = _inputs_digest(d)
        _write(d)
        _arm("MUTATION: the certificate carries the endTime of the level ABOVE "
             "-> REFUSE", lambda: read_certificate(cert, "L1"), True, fails,
             "REGISTERED-LADDER", verbose=verbose)
        _write(doc)
        _arm("MUTATION: read at the wrong level -> REFUSE",
             lambda: read_certificate(cert, "L2"), True, fails, "certifies level",
             verbose=verbose)
        _arm("NEGATIVE CONTROL: the untouched certificate still passes, so the "
             "refusals above are the mutations and not the reader",
             lambda: read_certificate(cert, "L1"), False, fails, verbose=verbose)

        # ---- 6. section 13.7's checkMesh command-line requirement ----------
        say("-- section 13.7: the log must prove which instrument produced it --")
        good = os.path.join(tmp, "log.good")
        open(good, "w").write("CHECKMESH COMMAND LINE: checkMesh -allRegions "
                              "-allGeometry -allTopology\nMesh OK.\n")
        _arm("CONTROL: a log recording the full check set is ACCEPTED",
             lambda: read_checkmesh_summary(good), False, fails, verbose=verbose)
        bare = os.path.join(tmp, "log.bare")
        open(bare, "w").write("CHECKMESH COMMAND LINE: checkMesh\nMesh OK.\n")
        _arm("MUTATION: a log produced by BARE checkMesh -> REFUSE",
             lambda: read_checkmesh_summary(bare), True, fails, "allGeometry",
             verbose=verbose)
        nocmd = os.path.join(tmp, "log.nocmd")
        open(nocmd, "w").write("Mesh OK.\n")
        _arm("MUTATION: a log recording NO command line -> REFUSE",
             lambda: read_checkmesh_summary(nocmd), True, fails, "no command line",
             verbose=verbose)
    finally:
        _sh.rmtree(tmp, ignore_errors=True)

    say("=" * 74)
    say("MESH SELFTEST %s (%d failed)%s"
        % ("PASS" if not fails else "FAIL", len(fails),
           "" if not fails else ": " + "; ".join(fails)))
    return EXIT_OK if not fails else 1


def _envelope_mutant(surf, text):
    """Drive the envelope refusal by shrinking the duct body out from under its
    own seed, so the seed ends up in the scaffolding exactly as the probe's did."""
    s2 = dict(surf)
    c2 = dict(surf["comps_obj"])
    d2 = dict(c2["duct"])
    d2["tris"] = d2["tris"] * 0.5           # duct shrinks; the seed stays put
    c2["duct"] = d2
    s2["comps_obj"] = c2
    s2["env_tris_obj"] = surf["env_tris_obj"] * 0.5
    return derive_seeds(s2, reg_regions(text), verbose=False)


def _seed_mutant(surf, text):
    """Drive derive_seeds' refusal by making `housing`'s seed land in `core`."""
    s = dict(surf)
    s["core_profile"] = [[x, r * 3.0] for x, r in surf["core_profile"]]
    return derive_seeds(s, reg_regions(text), verbose=False)


def main(argv):
    if "--selftest" in argv:
        rc = selftest()
        print("")
        return max(rc, mesh_selftest())
    if "--mesh-selftest" in argv:
        return mesh_selftest()

    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default

    try:
        if "--read-certificate" in argv:
            p = os.path.abspath(opt("--read-certificate"))
            doc = read_certificate(p, level=opt("--level"))
            print("BIRTH CERTIFICATE ACCEPTED: %s" % p)
            print("  level %s | surface %s | regions %s | cells %s | "
                  "level0Edge %s m" %
                  (doc["level"], doc["surface"]["sha256"][:16],
                   doc["built"]["regions"], doc["built"]["cells_total"],
                   doc["built"].get("level0Edge_m")))
            return EXIT_OK
        if "--certify" in argv:
            level = opt("--level")
            mdir = opt("--mesh-dir")
            if not level or not mdir:
                return refuse("--certify needs --level and --mesh-dir")
            p, _ = certify(level, os.path.abspath(mdir), out_path=opt("--out"))
            print("BIRTH CERTIFICATE WRITTEN AND READ BACK: %s" % p)
            return EXIT_OK
        if "--mesh" in argv:
            level = opt("--level", "L1")
            so = opt("--seed-order")
            tw = opt("--throwaway-levels")
            ec = opt("--expect-cells")
            mesh(level, go=("--go" in argv), mesh_root=opt("--mesh-root"),
                 stl=opt("--stl"), foam_bashrc=opt("--foam-bashrc"),
                 seed_order=so.split(",") if so else None,
                 throwaway_levels=tw, expect_cells=ec)
            return EXIT_OK
    except Refused as exc:
        print("REFUSE: %s" % exc)
        return EXIT_REFUSE

    if "--case-dir" not in argv:
        print(__doc__)
        return EXIT_REFUSE
    case_dir = os.path.abspath(argv[argv.index("--case-dir") + 1])
    level = argv[argv.index("--level") + 1] if "--level" in argv else "L1"
    if level not in LEVELS:
        return refuse("%r is not a registered T26 level: %s" % (level, " ".join(LEVELS)))
    os.makedirs(case_dir, exist_ok=True)
    why = preflight(case_dir)
    if why:
        for w in why:
            print("REFUSE: " + w)
        return EXIT_REFUSE
    return stage(case_dir, level, overwrite_orig="--overwrite-orig" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
