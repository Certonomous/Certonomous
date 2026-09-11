#!/usr/bin/env python3
"""CONTRACT CHECKER FOR d8g_runScript.py -- the D8G producer script.

PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.

WHY THIS IS A SEPARATE FILE, WHICH IS THE FIRST THING TO UNDERSTAND ABOUT IT.
`d8g_runScript.py` is a BYTE COPY of `curriculum_D8R/d8r_runScript.py`, which is itself a
byte copy of D8's frozen `opt/runScript.py`.  All three hash to
`28c7819487a025a5f6554d38062a2b66`.  PREREGISTRATION.md:316 registers this in as many
words -- *"because D8G's producer is D8R's and a family whose acceptance rule changes
between levels is not a family"* -- so the producer is not this lane's to design, and a
`--selftest` INSIDE it would break the byte identity that is its entire provenance.  The
test therefore lives here, outside it, and the file it tests is passed in by path.

WHAT IT CHECKS, AND WHY EACH ONE IS A REAL FAILURE MODE.  `d8g_of.py` does not import this
producer; it `exec`s the slice ABOVE the anchor `# OpenMDAO setup` and then reaches into
the resulting namespace for `Top` and `daOptions`.  That is a contract with three ways to
fail silently:
  (1) THE SPLIT.  If `class Top` or `daOptions` sat BELOW the anchor, the exec would
      succeed and the lookup would KeyError after the container had already started.  If
      `om.Problem()` or `prob.setup()` sat ABOVE it, the header exec would build a second
      Problem -- and on this case would also write `mphys.html` -- before `d8g_of.py` built
      its own.
  (2) THE ACCEPTANCE PAIR.  `primalMinResTol` and `primalMinResTolDiff` are read back out
      of the arm's own log by the comparator's `G-PRIMAL`, and A MISMATCH IS A GRADER
      REFUSAL, NOT A SOFT NOTE.  A6 carries TWO different `primalMinResTolDiff` values --
      10000 in this producer and 100 in the archived tutorial `runScript.py`
      (md5 `0de915d21166a91a9a54b37ab11214cf`), which sits in the SAME staging tree and
      which `d8g_run_arm.sh` deletes before staging this one.  Staging the wrong file is a
      live confusion and is checked for BY MD5 below, not by eye.
  (3) THE DESIGN VARIABLES.  The comparator's `read_A` requires `adjoint.{CD,CL}.{twist,
      patchV}` and indexes `twist` up to 5, with `twist[6]` NOT A RESULT BY NAME.  Those
      indices are well-formed only if the FFD gives the family its usual 7 twist
      components, AT EVERY LEVEL.

THE VALUES ARE EXTRACTED BY AST, NEVER BY REGEX.  A regex over source text cannot tell a
value inside `daOptions` from the same characters inside a comment or a sibling dict, and
this file's whole job is to be the thing that does not get that wrong.

WHAT IT DOES NOT CHECK, STATED PLAINLY.  It does not import DAFoam, IDWarp, mphys, pyGeo or
OpenMDAO -- none is installed outside the container -- so IT NEVER EXECUTES THE HEADER.  It
proves the header COMPILES and that the objects `d8g_of.py` reaches for are defined in the
right half of the file; it does NOT prove that `DAFoamBuilder` accepts these options, that
`nom_addRefAxis` returns 8, or that the L1 surface supports a 25x30 thickness-constraint
projection.  THOSE REMAIN UNTESTED UNTIL AN ARM RUNS, and they are named again at the foot
of this file's own output so nobody reads a green as covering them.

L-332: no `assert` anywhere; the census is a unit.  Verdict vocabulary is not used at all --
this instrument renders no verdicts, it reports units.

usage: d8g_runScript_contract.py [--target <runScript path>] [--of <d8g_of.py path>]
"""
import ast
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TARGET = os.path.join(HERE, "d8g_runScript.py")
DEFAULT_OF = os.path.join(HERE, "d8g_of.py")

ANCHOR = "# OpenMDAO setup"
# The three-way byte identity.  D8 -> D8R -> D8G, one md5.
FROZEN_PRODUCER_MD5 = "28c7819487a025a5f6554d38062a2b66"
D8R_PRODUCER = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_runScript.py"
D8_PRODUCER = "/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/opt/runScript.py"
# THE WRONG FILE, NAMED SO IT CAN BE REFUSED BY MD5 RATHER THAN BY EYE.
ARCHIVE_TUTORIAL = "/home/ubuntu/certonomous-runs/A6-crm-wing/runScript.py"
ARCHIVE_TUTORIAL_MD5 = "0de915d21166a91a9a54b37ab11214cf"
FFD_D8 = "/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/base/FFD/wingFFD.xyz"
FFD_ARCHIVE = "/home/ubuntu/certonomous-runs/A6-crm-wing/FFD/wingFFD.xyz"

REGISTERED = {"solverName": "DARhoSimpleCFoam", "primalMinResTol": 1.0e-8,
              "primalMinResTolDiff": 1.0e4, "primalMinIters": 1000, "printInterval": 10}
ACCEPT_FLOOR = 1.0e-4                               # the comparator's, = the product
REGISTERED_ENDTIME, REGISTERED_DELTAT = 1000.0, 1.0
DESIGN_SURFACES = ["wing"]
DVS_REQUIRED = ("twist", "patchV")
FUNCTIONS_REQUIRED = ("CD", "CL")
TWIST_COMPONENTS_REGISTERED = [0, 1, 3, 4, 5]       # d8g_grade.COMPONENTS_REGISTERED, twist half
TWIST_UNTOUCHED_BY_NAME = 6                         # D8 section 6: NOT A RESULT BY NAME
EXPECTED_UNITS = 27
NOT_MEASURED = "NOT_MEASURED"


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def split_on_anchor(src):
    """Exactly the split d8g_of.py performs.  Returns (header, n_anchors)."""
    n = src.count(ANCHOR)
    return (src.split(ANCHOR)[0] if n >= 1 else None), n


def _const(node):
    """The literal value of an AST node, or a sentinel for anything that is not a literal.
    Unary minus is handled because `-1.0e-8` is a UnaryOp, not a Constant, and a checker
    that missed that would silently skip every negative registered value."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        inner = _const(node.operand)
        return -inner if isinstance(inner, (int, float)) else _NOTLIT
    if isinstance(node, ast.List):
        return [_const(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {_const(k): _const(v) for k, v in zip(node.keys, node.values)}
    return _NOTLIT


class _NotLit(object):
    def __repr__(self):
        return "<not-a-literal>"


_NOTLIT = _NotLit()


def extract_daoptions(tree):
    """The `daOptions = {...}` literal, BY AST.  A regex over source text cannot tell a
    value inside this dict from the same characters in a comment or a sibling dict."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "daOptions" and isinstance(node.value, ast.Dict):
                    return _const(node.value)
    return None


def top_level_names(tree):
    out = {"classes": set(), "assigns": set()}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            out["classes"].add(node.name)
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    out["assigns"].add(t.id)
    return out


def calls_named(tree, dotted):
    """Every call in `tree` whose callee renders as `dotted` (e.g. `om.Problem`)."""
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                if "%s.%s" % (f.value.id, f.attr) == dotted:
                    found.append(node)
            elif isinstance(f, ast.Name) and f.id == dotted:
                found.append(node)
            elif isinstance(f, ast.Attribute) and f.attr == dotted.split(".")[-1] \
                    and dotted.count(".") == 0:
                found.append(node)
    return found


def string_args_of(tree, method):
    """First string argument of every `<anything>.<method>(...)` call -- used for
    add_design_var / add_output / nom_addGlobalDV, whose receivers differ."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == method:
            if node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                out.append(node.args[0].value)
            for kw in node.keywords:
                if kw.arg in ("dvName", "name") and isinstance(kw.value, ast.Constant):
                    out.append(kw.value.value)
    return out


def read_plot3d_dims(path):
    """A PLOT3D FFD: a block count, then one `ni nj nk` line per block.  Returns the first
    block's (ni, nj, nk), or None.  READ FROM THE FILE, not assumed from the family."""
    with open(path, errors="replace") as fh:
        head = [fh.readline() for _ in range(3)]
    try:
        nblk = int(head[0].split()[0])
        dims = [int(v) for v in head[1].split()[:3]]
    except (ValueError, IndexError):
        return None
    if nblk != 1 or len(dims) != 3:
        return None
    return tuple(dims)


def load_of_module(path):
    """Load d8g_of.py so the producer can be checked against THE PRODUCER'S OWN registered
    constants rather than a second copy of them.  Bytecode caching is suppressed: a stale
    `__pycache__` in a case directory inverts exactly the mutation controls these suites
    depend on, and it is clutter where nothing but the case belongs."""
    import importlib.machinery
    import importlib.util
    if not os.path.isfile(path):
        return None
    sys.dont_write_bytecode = True
    loader = importlib.machinery.SourceFileLoader("d8g_of_contract", path)
    spec = importlib.util.spec_from_loader("d8g_of_contract", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def run(target, of_path):
    n, fails, notes = 0, [], []

    def unit(name, cond):
        nonlocal n
        n += 1
        ok = cond is True
        if not ok:
            fails.append(name)
        print("  [%s] %s" % ("OK " if ok else "BAD", name))

    if not os.path.isfile(target):
        print("REFUSE target not found: %s" % target)
        return 2
    src = open(target).read()
    print("  target = %s" % target)
    print("  md5    = %s" % md5_of(target))

    # ---- A. PROVENANCE: the byte identity IS the registration -----------------------
    unit("U1 the producer hashes to the frozen D8 -> D8R -> D8G md5 %s" % FROZEN_PRODUCER_MD5,
         md5_of(target) == FROZEN_PRODUCER_MD5)
    if os.path.isfile(D8R_PRODUCER):
        unit("U2 byte-identical to curriculum_D8R/d8r_runScript.py (FROZEN, graded two-row PASS)",
             md5_of(target) == md5_of(D8R_PRODUCER))
    else:
        unit("U2 byte-identical to D8R's producer", False)
    if os.path.isfile(D8_PRODUCER):
        unit("U3 byte-identical to D8's own frozen opt/runScript.py -- a THREE-WAY identity",
             md5_of(target) == md5_of(D8_PRODUCER))
    else:
        notes.append("U3 D8's opt/runScript.py unreachable -> the three-way identity is %s" % NOT_MEASURED)
        unit("U3 D8's opt/runScript.py reachable for the three-way identity (else NOT_MEASURED, "
             "disclosed)", False)
    unit("U4 the producer is NOT the archived A6 tutorial runScript -- THE WRONG FILE, which "
         "carries a different acceptance pair and sits in the same staging tree",
         md5_of(target) != ARCHIVE_TUTORIAL_MD5)

    # ---- B. THE SPLIT d8g_of.py PERFORMS --------------------------------------------
    header, n_anchor = split_on_anchor(src)
    unit("U5 the anchor %r occurs EXACTLY ONCE (d8g_of.py refuses otherwise)" % ANCHOR, n_anchor == 1)
    htree = None
    if header is not None:
        try:
            compile(header, target, "exec")
            htree = ast.parse(header)
            unit("U6 the header slice COMPILES on its own", True)
        except SyntaxError as exc:
            unit("U6 the header slice COMPILES on its own", False)
            notes.append("U6 SyntaxError: %s" % exc)
    else:
        unit("U6 the header slice COMPILES on its own", False)
    names = top_level_names(htree) if htree else {"classes": set(), "assigns": set()}
    unit("U7 `class Top` is defined ABOVE the anchor -- d8g_of.py reads ns['Top']",
         "Top" in names["classes"])
    unit("U8 `daOptions` is assigned ABOVE the anchor -- d8g_of.py reads ns['daOptions']",
         "daOptions" in names["assigns"])
    unit("U9 `meshOptions` is assigned ABOVE the anchor (Top's builder consumes it)",
         "meshOptions" in names["assigns"])
    unit("U10 the header builds NO om.Problem -- it must not construct a second one before "
         "d8g_of.py builds its own", htree is not None and not calls_named(htree, "om.Problem"))
    unit("U11 the header calls NO prob.setup and NO om.n2 -- the header exec must not run "
         "setup, and must not write mphys.html into a cold-started arm",
         htree is not None and not calls_named(htree, "om.n2")
         and not any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                     and x.func.attr == "setup" and isinstance(x.func.value, ast.Name)
                     and x.func.value.id == "prob" for x in ast.walk(htree)))
    unit("U12 the header PRINTS NOTHING -- G-PRIMAL and G-PLAT read the SOLVER'S own stdout "
         "and a producer line could be parsed as solver output",
         htree is not None and not [c for c in ast.walk(htree)
                                    if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                                    and c.func.id == "print"])
    # d8g_of.py substitutes sys.argv before the exec; a header that BRANCHED on the parsed
    # args would silently take a different path than the one the arm intended.
    used_args = htree is not None and any(
        isinstance(x, ast.Name) and x.id == "args" and isinstance(x.ctx, ast.Load)
        for x in ast.walk(htree))
    unit("U13 the header never CONSUMES the parsed args -- d8g_of.py substitutes sys.argv, "
         "and a header that branched on it would take a path the arm did not choose",
         not used_args)

    # ---- C. THE ACCEPTANCE PAIR, BY AST ---------------------------------------------
    dao = extract_daoptions(htree) if htree else None
    unit("U14 `daOptions` is a literal dict this checker can read BY AST, not by regex",
         isinstance(dao, dict))
    d = dao if isinstance(dao, dict) else {}
    unit("U15 solverName == %s" % REGISTERED["solverName"], d.get("solverName") == REGISTERED["solverName"])
    unit("U16 primalMinResTol == 1.0e-08",
         isinstance(d.get("primalMinResTol"), float) and abs(d["primalMinResTol"] - REGISTERED["primalMinResTol"]) <= 1e-20)
    unit("U17 primalMinResTolDiff == 10000 -- NOT the archived tutorial's 100, which would "
         "make the accept floor 1e-06 and the comparator REFUSE on read-back",
         isinstance(d.get("primalMinResTolDiff"), (int, float))
         and abs(float(d["primalMinResTolDiff"]) - REGISTERED["primalMinResTolDiff"]) <= 1e-6)
    unit("U18 their PRODUCT is the comparator's ACCEPT_FLOOR 1.0e-4",
         isinstance(d.get("primalMinResTol"), float) and isinstance(d.get("primalMinResTolDiff"), (int, float))
         and abs(float(d["primalMinResTol"]) * float(d["primalMinResTolDiff"]) - ACCEPT_FLOOR) <= 1e-18)
    unit("U19 printInterval == 10 -- the cadence G-PLAT's window is forecast from",
         d.get("printInterval") == REGISTERED["printInterval"])
    unit("U20 primalMinIters == 1000", d.get("primalMinIters") == REGISTERED["primalMinIters"])
    unit("U21 designSurfaces == %s -- the patch name the mesh record registers" % DESIGN_SURFACES,
         d.get("designSurfaces") == DESIGN_SURFACES)
    fn = d.get("function") if isinstance(d.get("function"), dict) else {}
    unit("U22 daOptions['function'] defines BOTH graded functionals %s -- section 4.6 grades "
         "CD AND CL" % (FUNCTIONS_REQUIRED,),
         all(k in fn for k in FUNCTIONS_REQUIRED))
    unit("U23 both functionals name patchVelocityInputName 'patchV' -- the second design "
         "variable the comparator's read_A requires",
         all(isinstance(fn.get(k), dict) and fn[k].get("patchVelocityInputName") == "patchV"
             for k in FUNCTIONS_REQUIRED))

    # ---- D. THE DESIGN VARIABLES read_A INDEXES -------------------------------------
    dvs = set(string_args_of(htree, "add_design_var")) if htree else set()
    outs = set(string_args_of(htree, "add_output")) if htree else set()
    gdv = set(string_args_of(htree, "nom_addGlobalDV")) if htree else set()
    unit("U24 both %s are design variables AND dvs outputs -- read_A requires "
         "adjoint.{CD,CL}.{twist,patchV}" % (DVS_REQUIRED,),
         all(k in dvs for k in DVS_REQUIRED) and all(k in outs for k in DVS_REQUIRED)
         and "twist" in gdv)

    # ---- E. THE FFD, MEASURED, AND THE TWIST INDICES IT MAKES WELL-FORMED -----------
    if os.path.isfile(FFD_D8) and os.path.isfile(FFD_ARCHIVE):
        unit("U25 the FFD is byte-identical on BOTH staging paths (D8's base and the A6 "
             "archive d8g_genmesh.sh copies from) -- so the twist DVs cannot depend on which "
             "path staged the case", md5_of(FFD_D8) == md5_of(FFD_ARCHIVE))
        dims = read_plot3d_dims(FFD_ARCHIVE)
        n_twist = (dims[1] - 1) if dims else None
        unit("U26 the FFD is one PLOT3D block of 12 x 8 x 2, so alignIndex 'j' gives 8 ref-axis "
             "points and `twist` has 8-1 = 7 entries; every registered index %s is < 7 and "
             "index %d exists and is NOT in the registered set, so 'twist[6] is NOT A RESULT "
             "BY NAME' is a well-formed claim at EVERY level (the FFD does not depend on the "
             "mesh)" % (TWIST_COMPONENTS_REGISTERED, TWIST_UNTOUCHED_BY_NAME),
             dims == (12, 8, 2) and n_twist == 7
             and all(i < n_twist for i in TWIST_COMPONENTS_REGISTERED)
             and TWIST_UNTOUCHED_BY_NAME < n_twist
             and TWIST_UNTOUCHED_BY_NAME not in TWIST_COMPONENTS_REGISTERED)
        notes.append("U26 CAVEAT: that alignIndex 'j' yields nRefAxPts == the j-dimension is an "
                     "INFERENCE about pyGeo's semantics, NOT a measurement of pyGeo.  What IS "
                     "measured is the FFD's 12x8x2 shape and the source line `value=np.array([0] * "
                     "(nRefAxPts - 1))`; 8-1 = 7 agrees with the 7 twist components D8 measured "
                     "and with the comparator's own fixture.  Three agreements, one inference.")
    else:
        unit("U25 the FFD is reachable on both staging paths", False)
        unit("U26 the FFD dimensions make the registered twist indices well-formed", False)

    # ---- F. THE PRODUCER AND THE INSTRUMENT AGREE, driven through d8g_of.py ITSELF ---
    of = load_of_module(of_path)
    if of is None:
        unit("U27 d8g_of.py's OWN check_registered_daoptions() accepts this producer", False)
        notes.append("U27 d8g_of.py not found at %s -- the two halves of the contract were not "
                     "checked against each other" % of_path)
    else:
        bad = of.check_registered_daoptions(d)
        fc = of.forecast_plateau_window(REGISTERED_ENDTIME, REGISTERED_DELTAT,
                                        d.get("printInterval") or 0)
        unit("U27 d8g_of.py's OWN check_registered_daoptions() returns EMPTY on this producer, "
             "and its OWN plateau forecast gives %d samples / window %d >= 10 -- the producer "
             "and the instrument are checked against each other, not against two copies of the "
             "same table" % (fc["n_printed_samples_expected"], fc["plateau_window_expected"]),
             bad == [] and fc["sufficient"] is True
             and fc["n_printed_samples_expected"] == 101 and fc["plateau_window_expected"] == 11)
        if bad:
            notes.append("U27 departures: %r" % (bad,))

    # ---- L-332 -----------------------------------------------------------------------
    n_assert = sum(1 for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read()))
                   if isinstance(x, ast.Assert))
    n_assert_target = sum(1 for x in ast.walk(ast.parse(src)) if isinstance(x, ast.Assert))
    print("\n  ast.Assert census -- this checker: %d ; the producer: %d (L-332)"
          % (n_assert, n_assert_target))
    print("  UNITS RUN: %d (frozen count %d)" % (n, EXPECTED_UNITS))
    for note in notes:
        print("  NOTE: %s" % note)
    print("\n  NOT PROVED BY ANY GREEN ABOVE, NAMED SO IT CANNOT BE READ IN: this checker never "
          "executes the header.\n  It does not prove DAFoamBuilder accepts these options, that "
          "nom_addRefAxis returns 8, or that\n  the L1 surface (696 quads) supports the 25x30 "
          "thickness-constraint projection configure() runs.\n  THOSE ARE UNTESTED UNTIL AN ARM "
          "RUNS.")
    print("\nD8G RUNSCRIPT CONTRACT units=%d fails=%d" % (n, len(fails)))
    for f in fails:
        print("  FAILED UNIT: %s" % f)
    if n != EXPECTED_UNITS:
        print("  FAILED UNIT: the suite did not run its frozen unit count (%d != %d)" % (n, EXPECTED_UNITS))
        return 2
    return 2 if fails or n_assert else 0


def main(argv):
    target, of_path = DEFAULT_TARGET, DEFAULT_OF
    for i, a in enumerate(argv):
        if a == "--target" and i + 1 < len(argv):
            target = argv[i + 1]
        if a == "--of" and i + 1 < len(argv):
            of_path = argv[i + 1]
    return run(target, of_path)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
