#!/usr/bin/env python3
"""Cross-check every grader's DECLARED ``dim`` against the dimensionality its
mesh REPORTS.  A READER.  It refuses nothing and it arms nothing.

WHY THIS EXISTS
---------------
``scripts/roache_triple.py`` forms ``r = (N_fine/N_coarse) ** (1/dim)``, hence

    p = dim * ln|e32/e21| / ln(N_fine/N_coarse)

so THE OBSERVED ORDER IS PROPORTIONAL TO THE DECLARED ``dim``.  The module's
``require_dim`` (:203) refuses a MISSING ``dim`` -- it cannot verify a WRONG
one.  Declaring a 3D case ``dim = 2`` multiplies the reported order by 2/3:
a genuine p = 0.72 is reported as 0.48 and crosses ``STAGNANT_FLOOR = 0.5``,
flipping ``CONVERGING`` into ``STAGNANT`` and a result into ``NOT A RESULT``.

The mesh already states its own dimensionality.  ``checkMesh`` prints

    Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)

and, on the NEXT LINE, a different number about a different question

    Mesh has 3 solution (non-empty) directions (1 1 1)

VERIFICATION_CHARTER.md section 2bo.1's MEASURED trap was reading the wrong
one of those two lines.  This reader anchors on the literal token
``geometric (non-empty/wedge)`` and there is an executable selftest arm named
for section 2bo.1 that feeds it a log where the two lines DISAGREE.

Commissioned by VERIFICATION_CHARTER.md section 2cb finding 3 (v1.88), which
names it "a section 2bo reader, not a new gate, and it refuses nothing".

--------------------------------------------------------------------------
AUTHORITY -- THE BOUND ON THIS INSTRUMENT
--------------------------------------------------------------------------
D539 reserves the ADDING of a gate on lab process to Sanaa.  Therefore:

  * This reader EXITS 0 ON EVERY OUTCOME IT CAN REACH, disagreement included.
    Its exit code carries "THE READER RAN".  It NEVER carries "the corpus is
    clean".  A caller that treats exit 0 as a clean corpus has misread it;
    the census counts in the output are the finding, not the status.
  * A disagreement is printed as a DISCLOSURE, with both numbers and both
    paths.  It is NEVER labelled with a word from the fixed verdict
    vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
    PENDING).  This reader emits no verdict and moves no verdict.
  * It writes NO file into any graded tree and edits NO grader.  It opens
    files read-only.  If it finds a grader declaring the wrong ``dim``, that
    is a finding for the team that owns the grader; this reader does not fix
    it.
  * The ONLY non-zero exit is EXIT_OPERATIONAL (3): THIS READER'S OWN
    failure -- bad arguments, unreadable input, or the planted control not
    seen.  That path is STRUCTURAL, not a comment: every operational failure
    travels as ``OperationalFailure``, which is raised ONLY by argument
    handling and by the planted control.  Corpus findings travel as ``Row``
    objects in a ``Census`` and have no way to reach that exception.

--------------------------------------------------------------------------
EXIT-CODE CONTRACT
--------------------------------------------------------------------------
    0  EXIT_OK           the reader ran.  Says NOTHING about the corpus.
                         Emitted for AGREE, DISAGREE, DIM-UNRESOLVED,
                         MESH-UNRESOLVED, an empty corpus, all of them.
    3  EXIT_OPERATIONAL  the reader itself failed and produced no census:
                         bad arguments, unreadable root, or -- rule 3 --
                         the planted control was not seen.

--------------------------------------------------------------------------
THE PLANTED CONTROL (CLAUDE.md rule 3, NOT OPTIONAL)
--------------------------------------------------------------------------
"A zero from a reader not shown able to see a non-zero is not evidence."

Before any census is printed, this reader builds a synthetic case on disk --
a grader source declaring ``PLANT_DECLARED_DIM = 2`` beside a ``checkMesh``
log reporting ``PLANT_GEOMETRIC_DIRECTIONS = 3`` geometric directions -- and
reads it back THROUGH THE SAME ``resolve_declared_dim`` / 
``read_geometric_directions`` / ``compare_case`` CALL PATH the real corpus
uses.  If the planted disagreement is not seen, the reader REFUSES TO REPORT
and exits EXIT_OPERATIONAL.  The plant carries a distinctive token,
``PLANT_TOKEN``, so a plant row can never be mistaken for a corpus row.

--------------------------------------------------------------------------
HOW ``dim`` IS RESOLVED -- AND WHAT THAT READING IS WORTH
--------------------------------------------------------------------------
THIS IS A STATIC READING OF SOURCE TEXT.  NOTHING IS IMPORTED AND NOTHING IS
EVALUATED.  The reader parses each grader with ``ast`` and reports, for each
row, WHICH strategy resolved it:

  MODULE_CONST          a module-level ``DIM = 3`` / ``FOO_DIM = 2`` binding
                        to an integer literal.
  CALL_LITERAL          an integer literal passed as ``dim`` to one of
                        ``gci_equal`` / ``gci_unequal`` / ``representative_h``
                        / ``refinement_ratio`` / ``require_dim`` -- by keyword,
                        or positionally at that function's known index.
  CALL_VIA_MODULE_CONST ``dim=DIM`` where ``DIM`` is a module-level integer.
  CLI_DEFAULT           an ``add_argument("--dim", ..., default=<int>)``.
                        NOTE: the DEFAULT is what is read.  A run that passed
                        ``--dim`` on the command line overrode it and this
                        reader CANNOT SEE THAT.

A LOCALLY SHADOWED NAME IS NOT TRUSTED POSITIONALLY.  Measured in this
corpus: ``verification/runs/T-family/T3_runs/analyse_t3.py:337`` defines its
OWN ``gci_unequal(f_coarse, f_med, f_fine, r21, r32, fs=FS)`` -- the shared
name with NO ``dim`` parameter, where the shared module has ``dim`` at
position 5 and ``fs`` at 6.  Reading position 5 there would invent a
declaration out of that file's ``fs``.  Where a called name is DEFINED IN THE
SAME FILE, only an explicit ``dim=`` keyword is trusted and every other such
call is reported DIM-UNRESOLVED by name and line.

Everything else is DIM-UNRESOLVED, carried in the SAME output as the resolved
rows with its reason, and counted in the headline.  Section 2bn's lesson --
"A PROXY IS NOT THE PROPERTY" -- applies to this reader as much as to any
other: a function NAME is not a call, and a regex hit is not a declaration.
An AST call node IS a call, which is why ``ast`` is used instead of a regex;
but a STATIC call node is still not an EVALUATED argument, and every row says
so in its ``reading`` column: TEXTUAL(ast), never MEASURED.

A file that uses the module but declares no ``dim`` at all is counted
separately as NO-DIM-DECLARED.  It is NOT counted as agreement and NOT
counted as unresolved: nothing was declared, so nothing was read wrong.

--------------------------------------------------------------------------
HOW THE MESH IS READ
--------------------------------------------------------------------------
Any file whose NAME contains ``checkmesh`` (case-insensitively -- the corpus
holds ``log.checkMesh``, ``checkMesh_L1.log`` and
``CONTROL_nofill_L1_checkMesh.log``; section 2cc's third false zero of the
day was a case-sensitive ``find``).  The dimensionality is the integer in

    Mesh has <N> geometric (non-empty/wedge) directions

and NOT the integer in the ``solution`` line beneath it.  A log with no such
line is MESH-UNRESOLVED, reported, never guessed.  A log whose several
``geometric`` lines disagree (multi-region, several times) is
MESH-AMBIGUOUS: every value is printed and none is chosen.

THE ONE-CELL-THICK COLUMN, AND WHY IT DOES NOT OVERRIDE THE LINE.
Section 2cb's specimen ``A1WR`` records ``symmetry1 nFaces=130304`` against
130,304 cells -- nFaces == nCells, ONE CELL THICK -- and is classified 3D
only because it uses ``symmetry`` patches rather than ``empty``.  So this
reader reads BOTH: it reports the ``geometric`` line FAITHFULLY, and reports
``max(patch faces) == cells`` as a SEPARATE FLAGGED COLUMN (``1CELL``).
Where they disagree, BOTH are printed.  Reporting two disagreeing
measurements is correct; silently picking one is not.

--------------------------------------------------------------------------
HOW A GRADER IS LINKED TO A MESH -- THE WEAKEST JOINT, STATED FIRST
--------------------------------------------------------------------------
Section 2cc: "A CENSUS IS DEFINED BY ITS CORPUS AS MUCH AS BY ITS FILTER."
Two linkage rules are tried, and EVERY ROW SAYS WHICH ONE PRODUCED IT:

  ANCESTRY  checkMesh logs found under the grader's OWN directory subtree.
  STEM      the grader's directory basename with a trailing ``_runs``/``_run``
            stripped, matched as a path substring against every checkMesh log
            found anywhere in the roots.  Tried ONLY where ANCESTRY found
            nothing.  This exists because section 2cc's measured CRM false
            zero was a grader under ``cases/`` whose runs live under
            ``verification/runs/`` -- ancestry alone cannot see that pair.

A grader neither rule can link is MESH-UNRESOLVED.  STEM linkage is a
HEURISTIC and can mis-pair; rows carry ``link=STEM`` so a reader can discount
them.  This is the joint most likely to be wrong and it is named here first
rather than discovered later.

--------------------------------------------------------------------------
WHAT THIS READER CANNOT SEE
--------------------------------------------------------------------------
  * a ``dim`` computed at run time, passed on a command line, read from JSON
    at run time, or carried on an object attribute.  All DIM-UNRESOLVED.
  * whether the checkMesh log it read was produced by the mesh the grader
    actually graded.  It matches by PATH, never by mesh identity or mtime.
  * a mesh with no checkMesh log ever written.  MESH-UNRESOLVED.
  * corpora outside the roots it is given.  ``/home/ubuntu/certonomous-runs``
    is OUTSIDE git and holds real meshes (docs/LOCATIONS.md enumerates it);
    it is not a default root and must be passed explicitly.
  * A GRADER WITH ITS OWN LOCAL ROACHE IMPLEMENTATION.  ``cases/M6SR/
    analyse_m6sr.py:1738`` defines ``def roache_triple(f3, f2, f1, r)`` -- it
    takes ``r`` DIRECTLY and takes no ``dim`` at all, so it never reaches
    ``roache_triple.require_dim`` and has no declared ``dim`` for this reader
    to check.  Such files land in NO-DIM-DECLARED and, where a mesh is linked,
    are listed under THE BYPASS CLASS.  They cannot carry a wrong ``dim``;
    they carry the same error in a hand-computed ``r``, which is section
    2bo.2's falsifier and is OUT OF SCOPE HERE.
  * WHICH MESH LOGS NOTHING LINKED.  The headline carries a "checkMesh logs
    NEVER COMPARED" count.  On the measured corpus it is the LARGEST number
    in the output, and a zero DISAGREE count must be read against it.
  * whether a declared ``dim`` that AGREES with the mesh is CORRECT for the
    refinement family.  A genuinely 3D mesh refined in only two directions is
    section 2bo.2's falsifier and a DIFFERENT defect; this reader does not
    look for it and an AGREE row is not a clearance.

No bare ``assert`` appears anywhere in this file, selftest included --
``python3 -O`` strips them (scripts/case_protocol_freeze_hook.py:105).  A
selftest arm re-checks that structurally, on this file's own AST.
"""

import argparse
import ast
import os
import re
import shutil
import sys
import tempfile

# --------------------------------------------------------------------------
# exit-code contract -- see the module docstring
# --------------------------------------------------------------------------
EXIT_OK = 0            # THE READER RAN.  Says nothing about the corpus.
EXIT_OPERATIONAL = 3   # THIS READER failed.  Never reachable from a finding.

# --------------------------------------------------------------------------
# the planted control (CLAUDE.md rule 3) -- distinctive, and named in source
# --------------------------------------------------------------------------
PLANT_TOKEN = "PLANTED_DIM_DISAGREEMENT_7c3f91"
PLANT_DECLARED_DIM = 2
PLANT_GEOMETRIC_DIRECTIONS = 3

# The literal token that answers the dimensionality question, and the literal
# token of the neighbouring line that does NOT (section 2bo.1).
GEOMETRIC_TOKEN = "geometric (non-empty/wedge)"
SOLUTION_TOKEN = "solution (non-empty)"

RE_GEOMETRIC = re.compile(
    r"Mesh\s+has\s+(\d+)\s+geometric\s+\(non-empty/wedge\)\s+directions")
# Kept ONLY so a selftest arm can prove the reader does not use it.
RE_SOLUTION = re.compile(
    r"Mesh\s+has\s+(\d+)\s+solution\s+\(non-empty\)\s+directions")

RE_CELLS = re.compile(r"^\s*cells:\s*(\d+)\s*$")
RE_PATCH_ROW = re.compile(r"^\s{4}(\S+)\s+(\d+)\s+(\d+)\s+\S")

# roache_triple entry points that take a dimensionality, and the POSITIONAL
# index of ``dim`` in each (from scripts/roache_triple.py, read at source).
DIM_FUNCS = {
    "require_dim": 0,
    "representative_h": 1,       # (n_cells, dim, n_ref=1.0)
    "refinement_ratio": 2,       # (n_coarser, n_finer, dim)
    "gci_equal": 4,              # (f_coarse, f_med, f_fine, r, dim, fs=FS)
    "gci_unequal": 5,            # (f_c, f_m, f_f, r21, r32, dim, fs=FS)
}

RE_CONST_NAME = re.compile(r"^(DIM|DIM_[A-Z0-9_]+|[A-Z0-9_]+_DIM)$")
CHECKMESH_NAME = "checkmesh"


class OperationalFailure(Exception):
    """THIS READER failed.  Raised ONLY by argument handling and by the
    planted control.  NO corpus finding can raise it -- findings are ``Row``
    objects.  ``main`` maps it, and only it, to EXIT_OPERATIONAL."""


# ==========================================================================
# mesh side
# ==========================================================================
class MeshReading(object):
    def __init__(self, path):
        self.path = path
        self.geometric = []      # every ``geometric`` value found, in order
        self.solution = []       # read ONLY so the two can be reported apart
        self.cells = None
        self.max_patch_faces = None
        self.max_patch_name = None
        self.error = None

    @property
    def dim(self):
        """The single geometric value, or None where there is none or they
        disagree.  Disagreement is MESH-AMBIGUOUS and is never resolved by
        picking one."""
        uniq = sorted(set(self.geometric))
        return uniq[0] if len(uniq) == 1 else None

    @property
    def state(self):
        if self.error is not None:
            return "MESH-UNREADABLE"
        if not self.geometric:
            return "MESH-UNRESOLVED"
        if len(set(self.geometric)) > 1:
            return "MESH-AMBIGUOUS"
        return "MESH-OK"

    @property
    def one_cell_thick(self):
        """max(patch faces) == cells.  A separate measurement that NEVER
        overrides the geometric line (section 2cb, the A1WR specimen)."""
        if self.cells is None or self.max_patch_faces is None:
            return None
        return self.max_patch_faces == self.cells


def read_geometric_directions(path):
    """Read a checkMesh log.  Anchors on GEOMETRIC_TOKEN and NEVER on
    SOLUTION_TOKEN -- section 2bo.1's measured trap was reading the wrong one
    of two adjacent lines.  Read-only; never raises for a corpus file."""
    m = MeshReading(path)
    try:
        with open(path, "r", errors="replace") as fh:
            in_patch_table = False
            for line in fh:
                hit = RE_GEOMETRIC.search(line)
                if hit:
                    m.geometric.append(int(hit.group(1)))
                    continue
                hit = RE_SOLUTION.search(line)
                if hit:
                    m.solution.append(int(hit.group(1)))
                    continue
                hit = RE_CELLS.match(line)
                if hit and m.cells is None:
                    m.cells = int(hit.group(1))
                    continue
                if "Surface topology" in line:
                    in_patch_table = True
                    continue
                if in_patch_table:
                    row = RE_PATCH_ROW.match(line.rstrip("\n"))
                    if row is None:
                        if line.strip() == "":
                            in_patch_table = False
                        continue
                    faces = int(row.group(2))
                    if m.max_patch_faces is None or faces > m.max_patch_faces:
                        m.max_patch_faces = faces
                        m.max_patch_name = row.group(1)
    except OSError as exc:
        m.error = str(exc)
    return m


def find_checkmesh_logs(root):
    """Every file whose NAME contains 'checkmesh', CASE-INSENSITIVELY.
    Section 2cc, measured three times in one day: a case-sensitive name match
    returns a confident zero that reads as a finding."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "processor0",
                                    "node_modules")
                       and not d.startswith("processor")]
        for name in filenames:
            if CHECKMESH_NAME in name.lower():
                out.append(os.path.join(dirpath, name))
    return out


# ==========================================================================
# grader side -- a STATIC AST reading.  Nothing is imported or evaluated.
# ==========================================================================
class DimDeclaration(object):
    def __init__(self, value, strategy, lineno, text):
        self.value = value          # int, or None where unresolved
        self.strategy = strategy
        self.lineno = lineno
        self.text = text            # the source line, stripped


class GraderReading(object):
    def __init__(self, path):
        self.path = path
        self.declarations = []      # resolved DimDeclaration
        self.unresolved = []        # DimDeclaration with value None + reason
        self.error = None

    @property
    def values(self):
        return sorted(set(d.value for d in self.declarations))

    @property
    def state(self):
        if self.error is not None:
            return "DIM-UNPARSEABLE"
        if self.declarations:
            return "DIM-OK" if len(self.values) == 1 else "DIM-MULTIPLE"
        if self.unresolved:
            return "DIM-UNRESOLVED"
        return "NO-DIM-DECLARED"


def _func_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _int_literal(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, int) \
            and not isinstance(node.value, bool):
        return node.value
    return None


def _describe(node):
    try:
        return ast.unparse(node)
    except Exception:                                    # pragma: no cover
        return type(node).__name__


def resolve_declared_dim(path, source=None):
    """Resolve the ``dim`` a grader DECLARES, from its source text alone.

    THE READING IS TEXTUAL(ast): the AST node IS a call (not a regex hit on a
    function name -- section 2bn), but a STATIC argument is not an EVALUATED
    one.  Anything not resolvable to an integer literal is recorded as
    UNRESOLVED with its reason and is NEVER silently treated as agreement."""
    g = GraderReading(path)
    if source is None:
        try:
            with open(path, "r", errors="replace") as fh:
                source = fh.read()
        except OSError as exc:
            g.error = "unreadable: %s" % exc
            return g
    lines = source.splitlines()

    def src_line(lineno):
        return lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        g.error = "SyntaxError: %s" % exc
        return g

    if not uses_roache(tree):
        return g       # a MENTION is not a USE -- section 2bn, see uses_roache

    # --- strategy MODULE_CONST -------------------------------------------
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            val = _int_literal(node.value)
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and RE_CONST_NAME.match(tgt.id):
                    if val is not None:
                        consts[tgt.id] = val
                        g.declarations.append(DimDeclaration(
                            val, "MODULE_CONST", node.lineno,
                            src_line(node.lineno)))
                    else:
                        g.unresolved.append(DimDeclaration(
                            None, "MODULE_CONST/not-an-int-literal: %s"
                            % _describe(node.value), node.lineno,
                            src_line(node.lineno)))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) \
                and RE_CONST_NAME.match(node.target.id) and node.value is not None:
            val = _int_literal(node.value)
            if val is not None:
                consts[node.target.id] = val
                g.declarations.append(DimDeclaration(
                    val, "MODULE_CONST", node.lineno, src_line(node.lineno)))

    # --- LOCALLY SHADOWED NAMES ------------------------------------------
    # MEASURED IN THIS CORPUS: verification/runs/T-family/T3_runs/analyse_t3.py
    # :337 defines its OWN ``def gci_unequal(f_coarse, f_med, f_fine, r21,
    # r32, fs=FS)`` -- the SHARED name with a DIFFERENT SIGNATURE and NO
    # ``dim`` parameter, where the shared module has ``dim`` at position 5 and
    # ``fs`` at 6.  Applying the positional table to such a call would read
    # ``fs`` AS ``dim`` and invent a declaration that was never made.
    # verification/runs/navier_class/SUP_BOOSTER/grade_sup_booster.py:311 and
    # cases/M6SR/analyse_m6sr.py:1738 are the same shape.
    # Where a name is defined IN THIS FILE, only an explicit ``dim=`` KEYWORD
    # is trusted -- a keyword is unambiguous under any signature; a position
    # is not.
    local_defs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            local_defs.add(node.name)

    # --- strategies CALL_LITERAL / CALL_VIA_MODULE_CONST / CLI_DEFAULT ----
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fname = _func_name(node)

        if fname in DIM_FUNCS:
            arg = None
            for kw in node.keywords:
                if kw.arg == "dim":
                    arg = kw.value
            if arg is None:
                if fname in local_defs:
                    g.unresolved.append(DimDeclaration(
                        None, "%s is DEFINED IN THIS FILE with a possibly "
                        "different signature; the positional dim index of the "
                        "shared roache_triple.%s is NOT trusted here and no "
                        "dim= keyword was given" % (fname, fname),
                        node.lineno, src_line(node.lineno)))
                    continue
                idx = DIM_FUNCS[fname]
                if len(node.args) > idx:
                    arg = node.args[idx]
            if arg is None:
                continue                      # dim not given here; not a claim
            val = _int_literal(arg)
            if val is not None:
                g.declarations.append(DimDeclaration(
                    val, "CALL_LITERAL", node.lineno, src_line(node.lineno)))
            elif isinstance(arg, ast.Name) and arg.id in consts:
                g.declarations.append(DimDeclaration(
                    consts[arg.id], "CALL_VIA_MODULE_CONST", node.lineno,
                    src_line(node.lineno)))
            else:
                g.unresolved.append(DimDeclaration(
                    None, "%s(dim=%s): not an integer literal and not a "
                    "module-level constant this reader resolved"
                    % (fname, _describe(arg)), node.lineno,
                    src_line(node.lineno)))
            continue

        if fname == "add_argument":
            names = [a.value for a in node.args
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if not any(n in ("--dim", "-dim", "dim") for n in names):
                continue
            default = None
            for kw in node.keywords:
                if kw.arg == "default":
                    default = kw.value
            if default is None:
                g.unresolved.append(DimDeclaration(
                    None, "argparse --dim with no literal default; the value "
                    "came from the command line and this reader CANNOT SEE IT",
                    node.lineno, src_line(node.lineno)))
                continue
            val = _int_literal(default)
            if val is not None:
                g.declarations.append(DimDeclaration(
                    val, "CLI_DEFAULT", node.lineno, src_line(node.lineno)))
            else:
                g.unresolved.append(DimDeclaration(
                    None, "argparse --dim default=%s is not an integer literal"
                    % _describe(default), node.lineno, src_line(node.lineno)))
    return g


def find_graders(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "__pycache__", "node_modules")
                       and not d.startswith("processor")]
        for name in filenames:
            if name.endswith(".py"):
                out.append(os.path.join(dirpath, name))
    return out


# ==========================================================================
# linkage -- the weakest joint, named in every row
# ==========================================================================
def _stem(grader_path):
    base = os.path.basename(os.path.dirname(os.path.abspath(grader_path)))
    for suf in ("_runs", "_run"):
        if base.endswith(suf):
            base = base[:-len(suf)]
    return base


def link_meshes(grader_path, mesh_paths):
    """Return (list_of_mesh_paths, linkage_name).  ANCESTRY first; STEM only
    where ANCESTRY found nothing (section 2cc's CRM pair)."""
    gdir = os.path.dirname(os.path.abspath(grader_path)) + os.sep
    anc = [p for p in mesh_paths if os.path.abspath(p).startswith(gdir)]
    if anc:
        return anc, "ANCESTRY"
    stem = _stem(grader_path)
    if len(stem) >= 3:
        sep_stem = os.sep + stem
        hits = [p for p in mesh_paths if sep_stem in os.path.abspath(p)]
        if hits:
            return hits, "STEM"
    return [], "NONE"


# ==========================================================================
# the census -- findings travel ONLY here, and can never raise
# ==========================================================================
class Row(object):
    def __init__(self, state, grader, declared, mesh_path, geometric,
                 strategy, linkage, note=""):
        self.state = state          # AGREE / DISAGREE / DIM-* / MESH-*
        self.grader = grader
        self.declared = declared
        self.mesh_path = mesh_path
        self.geometric = geometric
        self.strategy = strategy
        self.linkage = linkage
        self.note = note


class Census(object):
    def __init__(self):
        self.rows = []

    def add(self, row):
        self.rows.append(row)

    def count(self, state):
        return sum(1 for r in self.rows if r.state == state)

    def of(self, state):
        return [r for r in self.rows if r.state == state]


def uses_roache(tree):
    """True where the file ACTUALLY CALLS or IMPORTS the Roache vocabulary.

    Section 2bn -- "A PROXY IS NOT THE PROPERTY".  An earlier draft of this
    reader tested ``"roache_triple" in source``, and a mere DOCSTRING MENTION
    in ``cases/F23_HP_WEDGE/exact_f23.py`` (a pure exact-solution module that
    grades nothing) was counted as a grader.  A substring hit is not a use.
    Membership is now an ast.Call node or an import statement."""
    names = set(DIM_FUNCS) | {"roache_triple"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _func_name(node) in names:
            return True
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[-1] == "roache_triple":
                    return True
        if isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[-1] == "roache_triple":
                return True
            for a in node.names:
                if a.name in names:
                    return True
    return False


def _by_value(declarations):
    """Group declarations by the integer they declare.  The census unit is a
    DISTINCT CLAIM, not a source line: ``DIM = 2`` plus ``gci_equal(..., DIM)``
    is ONE claim written twice, and counting it twice would inflate both the
    AGREE and the DISAGREE headline."""
    out = {}
    for d in declarations:
        out.setdefault(d.value, []).append(d)
    return out


def _sites(declarations):
    return ", ".join("%s:L%d" % (d.strategy, d.lineno) for d in declarations)


def compare_case(grader_path, mesh_paths, census, source=None):
    """Compare ONE grader against the meshes linked to it, appending rows.
    THIS FUNCTION NEVER RAISES OperationalFailure: a finding is a Row."""
    g = resolve_declared_dim(grader_path, source=source)

    if g.state == "NO-DIM-DECLARED":
        return g
    if g.state == "DIM-UNPARSEABLE":
        census.add(Row("DIM-UNRESOLVED", grader_path, None, None, None,
                       "UNPARSEABLE", "NONE", g.error))
        return g
    if g.state == "DIM-UNRESOLVED":
        for u in g.unresolved:
            census.add(Row("DIM-UNRESOLVED", grader_path, None, None, None,
                           "line %d" % u.lineno, "NONE", u.strategy))
        return g

    # resolved declarations exist; unresolved ones are STILL reported
    for u in g.unresolved:
        census.add(Row("DIM-UNRESOLVED", grader_path, None, None, None,
                       "line %d" % u.lineno, "NONE", u.strategy))

    if not mesh_paths:
        for val, sites in sorted(_by_value(g.declarations).items()):
            census.add(Row("MESH-UNRESOLVED", grader_path, val, None, None,
                           _sites(sites), "NONE",
                           "no checkMesh log linked by ANCESTRY or STEM"))
        return g

    for mp in sorted(mesh_paths):
        m = read_geometric_directions(mp)
        if m.state in ("MESH-UNRESOLVED", "MESH-UNREADABLE", "MESH-AMBIGUOUS"):
            census.add(Row(m.state if m.state != "MESH-UNREADABLE"
                           else "MESH-UNRESOLVED",
                           grader_path, g.values[0] if len(g.values) == 1
                           else g.values, mp, m.geometric or None,
                           _sites(g.declarations), "-",
                           m.error or ("no '%s' line" % GEOMETRIC_TOKEN
                                       if not m.geometric
                                       else "geometric lines disagree: %s"
                                       % m.geometric)))
            continue
        flag = ""
        if m.one_cell_thick:
            flag = ("1CELL max-patch '%s' nFaces=%d == cells=%d"
                    % (m.max_patch_name, m.max_patch_faces, m.cells))
        # ONE ROW PER DISTINCT DECLARED VALUE.  A grader that writes
        # ``DIM = 2`` and then ``gci_equal(..., DIM)`` has made ONE claim in
        # two places; counting it twice would inflate both the AGREE and the
        # DISAGREE headline.  Every site carrying the claim is still named in
        # the strategy column.
        for val, sites in sorted(_by_value(g.declarations).items()):
            state = "AGREE" if val == m.dim else "DISAGREE"
            note = flag
            if m.solution and len(set(m.solution)) == 1 \
                    and m.solution[0] != m.dim:
                note = (note + "  " if note else "") + \
                    ("solution line says %d (NOT the question -- 2bo.1)"
                     % m.solution[0])
            census.add(Row(state, grader_path, val, mp, m.dim,
                           _sites(sites), "-", note))
    return g


# ==========================================================================
# the planted control -- rule 3
# ==========================================================================
PLANT_GRADER_SRC = '''#!/usr/bin/env python3
"""{token} -- synthetic grader built by scripts/check_declared_dim.py.
Declares dim = {dim} against a mesh reporting {geo} geometric directions."""
from roache_triple import gci_equal

DIM = {dim}


def grade():
    return gci_equal(1.0, 1.1, 1.15, 2.0, DIM)
'''

PLANT_CHECKMESH = """Check mesh...

Mesh stats
    points:           1000
    faces:            2000
    internal faces:   1500
    cells:            800
    boundary patches: 2

Checking geometry...
    Mesh has {geo} geometric (non-empty/wedge) directions (1 1 1)
    Mesh has {geo} solution (non-empty) directions (1 1 1)
End
"""


def build_plant(root):
    """Write the synthetic planted case under ``root`` and return its dir."""
    d = os.path.join(root, "PLANTED_CONTROL_runs")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "grade_planted.py"), "w") as fh:
        fh.write(PLANT_GRADER_SRC.format(token=PLANT_TOKEN,
                                         dim=PLANT_DECLARED_DIM,
                                         geo=PLANT_GEOMETRIC_DIRECTIONS))
    with open(os.path.join(d, "log.checkMesh"), "w") as fh:
        fh.write(PLANT_CHECKMESH.format(geo=PLANT_GEOMETRIC_DIRECTIONS))
    return d


def run_plant_control():
    """Plant a KNOWN disagreement, read it back THROUGH THE SAME call path the
    corpus uses, and REFUSE TO REPORT if it is not seen (CLAUDE.md rule 3).

    Raises OperationalFailure -- the ONLY finding-shaped thing in this file
    allowed to do so, because it is a failure of THE READER, not of a corpus."""
    tmp = tempfile.mkdtemp(prefix="check_declared_dim_plant_")
    try:
        d = build_plant(tmp)
        grader = os.path.join(d, "grade_planted.py")
        meshes = find_checkmesh_logs(d)
        if not meshes:
            raise OperationalFailure(
                "PLANTED CONTROL NOT SEEN: the log walker found no checkMesh "
                "log in the planted case at %s.  A zero from this reader is "
                "not evidence." % d)
        linked, linkage = link_meshes(grader, meshes)
        if linkage != "ANCESTRY" or not linked:
            raise OperationalFailure(
                "PLANTED CONTROL NOT SEEN: linkage returned %r/%d for the "
                "planted case." % (linkage, len(linked)))
        c = Census()
        compare_case(grader, linked, c)
        dis = c.of("DISAGREE")
        ok = [r for r in dis
              if r.declared == PLANT_DECLARED_DIM
              and r.geometric == PLANT_GEOMETRIC_DIRECTIONS]
        if not ok:
            raise OperationalFailure(
                "PLANTED CONTROL NOT SEEN: planted declared dim=%d against %d "
                "geometric directions and the reader reported states %s.  "
                "A zero from a reader not shown able to see a non-zero is not "
                "evidence (CLAUDE.md rule 3).  REFUSING TO REPORT."
                % (PLANT_DECLARED_DIM, PLANT_GEOMETRIC_DIRECTIONS,
                   sorted(set(r.state for r in c.rows)) or ["<no rows>"]))
        return ok[0]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ==========================================================================
# reporting
# ==========================================================================
def emit(census, roots, plant_row, n_graders, n_meshes, n_nodecl,
         nodecl_with_mesh=(), n_uncompared=0):
    w = sys.stdout.write
    w("=" * 78 + "\n")
    w("DECLARED-dim vs checkMesh CROSS-CHECK -- A READER\n")
    w("  It REFUSES NOTHING, ARMS NO GATE and MOVES NO VERDICT (D539).\n")
    w("  Exit 0 means THE READER RAN.  It does NOT mean the corpus is clean.\n")
    w("  The reading is TEXTUAL(ast) for dim, PARSED for checkMesh.\n")
    w("=" * 78 + "\n")
    w("roots:\n")
    for r in roots:
        w("  %s\n" % r)
    w("\nPLANTED CONTROL (CLAUDE.md rule 3): SEEN -- declared dim=%d vs %d "
      "geometric directions,\n  read back as %s through the corpus call path. "
      "Token %s.\n\n"
      % (plant_row.declared, plant_row.geometric, plant_row.state, PLANT_TOKEN))

    w("CENSUS\n")
    w("  grader .py files walked ............ %d\n" % n_graders)
    w("  checkMesh-named logs found ......... %d\n" % n_meshes)
    w("  AGREE   (grader/mesh pairs) ........ %d\n" % census.count("AGREE"))
    w("  DISAGREE (grader/mesh pairs) ....... %d\n" % census.count("DISAGREE"))
    w("  DIM-UNRESOLVED ..................... %d   <- blind spot, not clean\n"
      % census.count("DIM-UNRESOLVED"))
    w("  MESH-UNRESOLVED .................... %d   <- blind spot, not clean\n"
      % census.count("MESH-UNRESOLVED"))
    w("  MESH-AMBIGUOUS ..................... %d\n"
      % census.count("MESH-AMBIGUOUS"))
    w("  NO-DIM-DECLARED (files, not rows) .. %d\n" % n_nodecl)
    w("  checkMesh logs NEVER COMPARED ...... %d   <- corpus blind spot\n"
      % n_uncompared)
    w("\n  The two UNRESOLVED counts are as much a finding as the DISAGREE\n"
      "  count: they are what this instrument CANNOT SEE.\n\n")

    def block(title, state, show_mesh=True):
        rows = census.of(state)
        w("-" * 78 + "\n%s  (%d)\n" % (title, len(rows)) + "-" * 78 + "\n")
        if not rows:
            w("  (none)\n\n")
            return
        for r in rows:
            w("  grader   : %s\n" % r.grader)
            w("  declared : %s   [%s]\n" % (r.declared, r.strategy))
            if show_mesh:
                w("  mesh     : %s\n" % r.mesh_path)
                w("  geometric: %s\n" % r.geometric)
            if r.note:
                w("  note     : %s\n" % r.note)
            w("\n")

    block("DISCLOSURE -- DECLARED dim DISAGREES WITH THE MESH", "DISAGREE")
    block("DIM-UNRESOLVED -- a declaration this reader could not read",
          "DIM-UNRESOLVED", show_mesh=False)
    block("MESH-UNRESOLVED -- no readable geometric-directions line",
          "MESH-UNRESOLVED")
    block("MESH-AMBIGUOUS -- several disagreeing geometric lines",
          "MESH-AMBIGUOUS")

    w("-" * 78 + "\nNO-DIM-DECLARED, YET A MESH IS LINKED -- THE BYPASS CLASS"
      "  (%d)\n" % len(nodecl_with_mesh) + "-" * 78 + "\n")
    w("  These files use the Roache vocabulary and have checkMesh logs beneath\n"
      "  them, but pass no ``dim`` to any entry point this reader knows.  The\n"
      "  usual cause is a LOCAL Roache implementation taking ``r`` directly,\n"
      "  which never reaches roache_triple.require_dim at all.  Such a case\n"
      "  cannot carry a WRONG ``dim`` -- it carries the same error in its\n"
      "  hand-computed ``r`` instead, which THIS READER DOES NOT CHECK and\n"
      "  which require_dim does not protect.  Listed, not judged.\n\n")
    if not nodecl_with_mesh:
        w("  (none)\n\n")
    for path, nm, geos in nodecl_with_mesh:
        w("  grader   : %s\n" % path)
        w("  meshes   : %d linked; geometric directions seen: %s\n\n"
          % (nm, geos))

    flagged = [r for r in census.of("AGREE") + census.of("DISAGREE")
               if "1CELL" in r.note]
    w("-" * 78 + "\nFLAG 1CELL -- max patch nFaces == cells (the A1WR shape)"
      "  (%d)\n" % len(flagged) + "-" * 78 + "\n")
    if not flagged:
        w("  (none)\n")
    for r in flagged:
        w("  %s\n    declared %s / geometric %s -- %s\n"
          % (r.mesh_path, r.declared, r.geometric, r.note))
    w("\n  The geometric line is reported FAITHFULLY above; this flag is a\n"
      "  SECOND measurement printed beside it and does NOT override it.\n")
    w("=" * 78 + "\n")
    w("THE READER RAN.  NO VERDICT WAS EMITTED AND NO GATE WAS ARMED.\n")
    w("=" * 78 + "\n")


# ==========================================================================
# selftest -- both arms, no bare assert anywhere
# ==========================================================================
def _fail(arm, msg):
    raise RuntimeError("SELFTEST ARM FAILED [%s]: %s" % (arm, msg))


def selftest():
    passed = []
    tmp = tempfile.mkdtemp(prefix="check_declared_dim_selftest_")
    try:
        # ARM 1 -- the planted disagreement is SEEN
        row = run_plant_control()
        if row.state != "DISAGREE" or row.declared != PLANT_DECLARED_DIM \
                or row.geometric != PLANT_GEOMETRIC_DIRECTIONS:
            _fail("plant-seen", "plant read back as %r" % row.state)
        passed.append("ARM 1 plant-seen: planted dim=2 vs 3 geometric "
                      "directions READ BACK as DISAGREE")

        # ARM 2 -- a matching pair reports AGREE
        d = os.path.join(tmp, "AGREE_runs")
        os.makedirs(d)
        with open(os.path.join(d, "g.py"), "w") as fh:
            fh.write("from roache_triple import gci_equal\nDIM = 3\n"
                     "x = gci_equal(1, 2, 3, 2.0, DIM)\n")
        with open(os.path.join(d, "log.checkMesh"), "w") as fh:
            fh.write(PLANT_CHECKMESH.format(geo=3))
        c = Census()
        compare_case(os.path.join(d, "g.py"),
                     find_checkmesh_logs(d), c)
        if c.count("AGREE") < 1 or c.count("DISAGREE") != 0:
            _fail("agree", "AGREE=%d DISAGREE=%d"
                  % (c.count("AGREE"), c.count("DISAGREE")))
        passed.append("ARM 2 agree: DIM=3 vs 3 geometric directions -> AGREE")

        # ARM 3 -- an unresolvable declaration is UNRESOLVED, NOT agreement
        d = os.path.join(tmp, "UNRES_runs")
        os.makedirs(d)
        with open(os.path.join(d, "g.py"), "w") as fh:
            fh.write("from roache_triple import gci_equal\n"
                     "import argparse\n"
                     "a = argparse.ArgumentParser()\n"
                     "a.add_argument('--dim', type=int)\n"
                     "ns = a.parse_args()\n"
                     "x = gci_equal(1, 2, 3, 2.0, dim=ns.dim)\n")
        with open(os.path.join(d, "log.checkMesh"), "w") as fh:
            fh.write(PLANT_CHECKMESH.format(geo=3))
        c = Census()
        compare_case(os.path.join(d, "g.py"), find_checkmesh_logs(d), c)
        if c.count("DIM-UNRESOLVED") < 1:
            _fail("unresolved", "no DIM-UNRESOLVED row emitted")
        if c.count("AGREE") != 0:
            _fail("unresolved", "an unresolvable declaration was counted as "
                               "AGREE -- the exact silent-pass this arm exists "
                               "to forbid")
        passed.append("ARM 3 unresolved: dim=ns.dim -> DIM-UNRESOLVED (%d "
                      "rows) and AGREE=0" % c.count("DIM-UNRESOLVED"))

        # ARM 4 -- section 2bo.1, THE WRONG-checkMesh-LINE TRAP, by name.
        #   solution says 3, geometric says 2; the reader MUST report 2.
        d = os.path.join(tmp, "TRAP_2bo1_runs")
        os.makedirs(d)
        trap = ("Mesh stats\n    cells:            800\n"
                "Checking geometry...\n"
                "    Mesh has 2 geometric (non-empty/wedge) directions (1 1 0)\n"
                "    Mesh has 3 solution (non-empty) directions (1 1 1)\n")
        trap_log = os.path.join(d, "log.checkMesh")
        with open(trap_log, "w") as fh:
            fh.write(trap)
        m = read_geometric_directions(trap_log)
        if m.dim != 2:
            _fail("2bo.1-wrong-line",
                  "reader returned %r; it read the SOLUTION line, which is "
                  "section 2bo.1's measured trap" % m.dim)
        if m.solution != [3]:
            _fail("2bo.1-wrong-line",
                  "solution line not captured for side-by-side reporting")
        with open(os.path.join(d, "g.py"), "w") as fh:
            fh.write("from roache_triple import gci_equal\nDIM = 2\n"
                     "x = gci_equal(1, 2, 3, 2.0, DIM)\n")
        c = Census()
        compare_case(os.path.join(d, "g.py"), find_checkmesh_logs(d), c)
        if c.count("AGREE") != 1 or c.count("DISAGREE") != 0:
            _fail("2bo.1-wrong-line",
                  "grader DIM=2 against geometric=2 should AGREE; got "
                  "AGREE=%d DISAGREE=%d -- reading the solution line would "
                  "have produced a FALSE DISAGREE"
                  % (c.count("AGREE"), c.count("DISAGREE")))
        passed.append("ARM 4 section-2bo.1 wrong-line trap: solution=3 / "
                      "geometric=2 -> reader reports 2, and the solution "
                      "value is carried beside it, never instead of it")

        # ARM 5 -- no mesh log linked -> MESH-UNRESOLVED, never guessed
        d = os.path.join(tmp, "NOMESH_runs")
        os.makedirs(d)
        with open(os.path.join(d, "g.py"), "w") as fh:
            fh.write("from roache_triple import gci_equal\nDIM = 3\n"
                     "x = gci_equal(1, 2, 3, 2.0, DIM)\n")
        c = Census()
        linked, _ = link_meshes(os.path.join(d, "g.py"), [])
        compare_case(os.path.join(d, "g.py"), linked, c)
        if c.count("MESH-UNRESOLVED") != 1 or c.count("AGREE") != 0:
            _fail("mesh-unresolved", "MESH-UNRESOLVED=%d AGREE=%d"
                  % (c.count("MESH-UNRESOLVED"), c.count("AGREE")))
        passed.append("ARM 5 mesh-unresolved: no checkMesh log -> "
                      "MESH-UNRESOLVED, not a guess and not an AGREE")

        # ARM 6 -- the 1CELL flag fires, and does NOT override the line
        d = os.path.join(tmp, "ONECELL_runs")
        os.makedirs(d)
        oc = ("Mesh stats\n    cells:            130304\n"
              "Checking geometry...\n"
              "    Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)\n"
              "Checking patch topology for multiply connected surfaces...\n"
              "    Patch               Faces    Points     Surface topology\n"
              "    symmetry1           130304   131000     ok (non-closed)\n"
              "    wing                509      600        ok (non-closed)\n")
        p = os.path.join(d, "log.checkMesh")
        with open(p, "w") as fh:
            fh.write(oc)
        m = read_geometric_directions(p)
        if m.one_cell_thick is not True:
            _fail("1cell", "flag did not fire on nFaces=%r cells=%r"
                  % (m.max_patch_faces, m.cells))
        if m.dim != 3:
            _fail("1cell", "the 1CELL flag OVERRODE the geometric line; it "
                           "must be reported beside it, never instead of it")
        passed.append("ARM 6 1CELL flag (the A1WR shape): nFaces==cells "
                      "FLAGGED while the geometric line still reads 3")

        # ARM 7 -- no bare assert survives in this file (python3 -O strips them)
        with open(os.path.abspath(__file__), "r") as fh:
            own = ast.parse(fh.read())
        bad = [n.lineno for n in ast.walk(own) if isinstance(n, ast.Assert)]
        if bad:
            _fail("no-bare-assert", "ast.Assert at lines %s" % bad)
        passed.append("ARM 7 no-bare-assert: zero ast.Assert nodes in this "
                      "file (python3 -O would strip them)")

        # ARM 8 -- the exit-code contract: a DISAGREEING corpus still exits 0
        d = build_plant(os.path.join(tmp, "EXITCONTRACT"))
        rc = run_census([os.path.join(tmp, "EXITCONTRACT")], quiet=True)
        if rc != EXIT_OK:
            _fail("exit-contract",
                  "a corpus containing a DISAGREEMENT exited %d; a finding "
                  "must NEVER move the exit code (D539)" % rc)
        passed.append("ARM 8 exit-contract: a corpus holding a DISAGREEMENT "
                      "still exits %d -- a finding never moves the exit code"
                      % EXIT_OK)

        # ARM 9 -- OperationalFailure is structurally unreachable from a finding
        srcs = []
        with open(os.path.abspath(__file__), "r") as fh:
            own2 = ast.parse(fh.read())
        for node in ast.walk(own2):
            if isinstance(node, ast.Raise) and node.exc is not None:
                nm = None
                if isinstance(node.exc, ast.Call):
                    nm = _func_name(node.exc)
                elif isinstance(node.exc, ast.Name):
                    nm = node.exc.id
                if nm == "OperationalFailure":
                    srcs.append(node.lineno)
        fn_of = {}
        for node in ast.walk(own2):
            if isinstance(node, ast.FunctionDef):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Raise):
                        fn_of[sub.lineno] = node.name
        raisers = sorted(set(fn_of.get(ln, "<module>") for ln in srcs))
        allowed = {"run_plant_control", "parse_roots"}
        stray = [r for r in raisers if r not in allowed]
        if stray:
            _fail("operational-isolation",
                  "OperationalFailure raised from %s; it must come ONLY from "
                  "the planted control and argument handling, never from a "
                  "corpus finding" % stray)
        passed.append("ARM 9 operational-isolation: OperationalFailure is "
                      "raised only from %s -- no corpus finding can reach "
                      "exit %d" % (sorted(allowed), EXIT_OPERATIONAL))

        # ARM 10 -- section 2bn: A MENTION IS NOT A USE.  A file that only
        #   NAMES the Roache vocabulary in a docstring is not a grader and
        #   must not enter any census bucket.  Measured on the real corpus:
        #   cases/F23_HP_WEDGE/exact_f23.py was wrongly listed as a grader by
        #   an earlier substring test in this very file.
        mention_only = ('"""This module mentions roache_triple and gci_equal '
                        'in prose only."""\nX = 1\n')
        g = resolve_declared_dim("<mention-only>", source=mention_only)
        if g.state != "NO-DIM-DECLARED" or g.declarations or g.unresolved:
            _fail("2bn-mention-is-not-a-use",
                  "a docstring MENTION was read as a declaration (%s)"
                  % g.state)
        if uses_roache(ast.parse(mention_only)):
            _fail("2bn-mention-is-not-a-use",
                  "uses_roache() accepted a prose mention as a use")
        real_use = ("from roache_triple import gci_equal\n"
                    "x = gci_equal(1, 2, 3, 2.0, 3)\n")
        if not uses_roache(ast.parse(real_use)):
            _fail("2bn-mention-is-not-a-use",
                  "uses_roache() rejected a REAL call -- the control proving "
                  "this arm can see a positive")
        passed.append("ARM 10 section-2bn mention-is-not-a-use: a prose "
                      "mention is NOT counted as a grader, and a real "
                      "gci_equal call still IS (both arms shown)")

        # ARM 11 -- LOCALLY SHADOWED NAME, the analyse_t3.py:337 shape.
        #   A file defining its OWN gci_unequal(f_c, f_m, f_f, r21, r32, fs)
        #   has NO dim at all; position 5 there is ``fs``.  The reader must
        #   NOT read 1.25 as a declared dim of 1.
        shadow = ("from roache_triple import gci_equal\n"
                  "FS = 1.25\n"
                  "def gci_unequal(f_c, f_m, f_f, r21, r32, fs=FS):\n"
                  "    return (f_c, f_m, f_f, r21, r32, fs)\n"
                  "x = gci_unequal(1.0, 2.0, 3.0, 2.0, 2.0, 1)\n")
        g = resolve_declared_dim("<shadow>", source=shadow)
        if any(d.value == 1 for d in g.declarations):
            _fail("local-shadow",
                  "read the 6th positional argument of a LOCALLY DEFINED "
                  "gci_unequal as a declared dim -- it is that file's ``fs``, "
                  "and the declaration was invented")
        if not g.unresolved:
            _fail("local-shadow", "the shadowed call was not reported as "
                                  "DIM-UNRESOLVED; it was silently dropped")
        # control: the SAME positional index IS trusted when not shadowed
        plain = ("from roache_triple import gci_unequal\n"
                 "x = gci_unequal(1.0, 2.0, 3.0, 2.0, 2.0, 3)\n")
        g2 = resolve_declared_dim("<plain>", source=plain)
        if g2.values != [3]:
            _fail("local-shadow",
                  "the control failed: an UNSHADOWED positional dim=3 must "
                  "still be read, else this arm proves only blindness")
        passed.append("ARM 11 local-shadow (the analyse_t3.py:337 shape): a "
                      "locally redefined gci_unequal does NOT have its ``fs`` "
                      "read as dim, and the unshadowed positional dim=3 IS "
                      "still read (control shown)")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("=" * 78)
    print("SELFTEST -- scripts/check_declared_dim.py")
    print("=" * 78)
    for line in passed:
        print("  PASS  " + line)
    print("-" * 78)
    print("  %d/%d arms passed." % (len(passed), len(passed)))
    print("  A passing selftest says THE READER WORKS.  It says nothing "
          "about any corpus.")
    print("=" * 78)
    return EXIT_OK


# ==========================================================================
# driver
# ==========================================================================
def parse_roots(roots):
    out = []
    for r in roots:
        a = os.path.abspath(r)
        if not os.path.isdir(a):
            raise OperationalFailure("not a directory: %s" % a)
        out.append(a)
    if not out:
        raise OperationalFailure("no roots given")
    return out


def run_census(roots, quiet=False):
    """Walk, compare, report.  Returns EXIT_OK for every corpus outcome."""
    roots = parse_roots(roots)
    plant_row = run_plant_control()          # rule 3, BEFORE anything is said

    meshes = []
    graders = []
    for r in roots:
        meshes.extend(find_checkmesh_logs(r))
        graders.extend(find_graders(r))
    meshes = sorted(set(meshes))
    graders = sorted(set(graders))

    census = Census()
    n_nodecl = 0
    n_roache = 0
    nodecl_with_mesh = []
    for gp in graders:
        linked, linkage = link_meshes(gp, meshes)
        before = len(census.rows)
        g = compare_case(gp, linked, census)
        if g.state == "NO-DIM-DECLARED":
            if g.error is None:
                try:
                    with open(gp, "r", errors="replace") as fh:
                        uses = uses_roache(ast.parse(fh.read()))
                except (OSError, SyntaxError):
                    uses = False
                if uses:
                    n_nodecl += 1
                    n_roache += 1
                    if linked:
                        geos = sorted(set(
                            d for d in (read_geometric_directions(p).dim
                                        for p in linked) if d is not None))
                        nodecl_with_mesh.append((gp, len(linked), geos))
            continue
        n_roache += 1
        for row in census.rows[before:]:
            row.linkage = linkage

    compared = set(r.mesh_path for r in census.rows if r.mesh_path)
    n_uncompared = len(meshes) - len(compared)

    if not quiet:
        emit(census, roots, plant_row, n_roache, len(meshes), n_nodecl,
             nodecl_with_mesh, n_uncompared)
    return EXIT_OK


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Cross-check each grader's DECLARED dim against the "
                    "dimensionality its checkMesh log REPORTS.  A READER: it "
                    "refuses nothing, arms no gate and moves no verdict. "
                    "Exit 0 means THE READER RAN, never 'the corpus is clean'.")
    ap.add_argument("roots", nargs="*",
                    help="directories to walk (default: verification/runs and "
                         "cases under the repo root)")
    ap.add_argument("--selftest", action="store_true",
                    help="run the selftest arms, including the planted "
                         "control and the section-2bo.1 wrong-line trap")
    args = ap.parse_args(argv)

    try:
        if args.selftest:
            return selftest()
        roots = args.roots
        if not roots:
            repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            roots = [os.path.join(repo, "verification", "runs"),
                     os.path.join(repo, "cases")]
        return run_census(roots)
    except OperationalFailure as exc:
        sys.stderr.write("OPERATIONAL FAILURE (exit %d): %s\n"
                         % (EXIT_OPERATIONAL, exc))
        sys.stderr.write("This is THIS READER failing, not a corpus finding. "
                         "No census was produced.\n")
        return EXIT_OPERATIONAL


if __name__ == "__main__":
    sys.exit(main())
