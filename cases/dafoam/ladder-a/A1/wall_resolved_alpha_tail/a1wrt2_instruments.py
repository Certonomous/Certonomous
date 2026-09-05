#!/usr/bin/env python3
"""a1wrt2_instruments.py -- THE INSTRUMENT TABLE, ENUMERATED BY EXTRACTION.

`DAFOAM_CHARTER.md` section 18.3, and `A1WRT2_SUCCESSOR_DRAFT.md` section 11
item 2.  NOT FROZEN.  NOT PINNED.  NO COMPUTE.  SUBMISSIONS PARKED.

THE SCAR THIS FILE IS BUILT ON, AND IT IS A SCAR RATHER THAN A STYLE PREFERENCE
------------------------------------------------------------------------------
`SO2a` (incident `SO2a-DRIVER-DEF-1`, 2026-08-30) froze eight instruments by md5
and its md5-agreement control read **eight of eight AGREE**, correctly.  The
question it asked -- *do the files I pinned still hash to what I pinned?* -- was
answered correctly.  The question nobody asked was *is everything the frozen code
RUNS actually present?*  `so2a_chain_driver.sh:143` executes

    AGG=$(python3 "$HERE/so2a_aggregate_memory.py" ...)

inside a 30-second poll loop, and that file was ABSENT from the freeze commit
`5f0e083e` -- `git cat-file -e 5f0e083e:<path>` fails on that tree, MEASURED in
this invocation.  Four hours of polling an empty result and a `BLOCKED` at the
first arm, with every control the item held reporting that all was well.

THESE ARE DIFFERENT QUESTIONS AND THE SECOND CANNOT BE INFERRED FROM THE FIRST
AT ANY LEVEL OF AGREEMENT -- not at 8 of 8, not at 800 of 800.  So this file
asserts EXISTENCE FIRST AND SEPARATELY, and the ordering is not a convention: no
md5 in this file can be computed until an `ExistenceTable` object exists, and
that object can only be constructed by the existence pass returning clean.  A
reader who wants to check the ordering reads `md5_table()`'s first statement.

WHY IT PARSES RATHER THAN READS A LIST
--------------------------------------
Section 18.3's sharpest sentence: SO2a *already had* a section 7.3, `WHAT IS NOT
DRIVEN, NAMED`, which honestly declared a DIFFERENT absent file.  The item had
the right instinct, wrote a whole section to serve it, and still missed the
dependency its own driver executes -- because a prose section names what its
author thought of, and the author thought of the selftest they had decided not
to run, not the helper they had decided to write and had not yet written.
**An enumeration derived from the code cannot have that failure mode.**

TRANSITIVE, TO A FIXED POINT, AND IT REFUSES RATHER THAN GUESSING A DEPTH
-------------------------------------------------------------------------
Each derived instrument is itself parsed, so `a1wrt2_stage.py` ->
`a1wrt2_grade.py` -> the nine `fixtures/` files is found by iteration and not by
someone remembering that the fixtures exist.  `derive()` runs rounds until the
set stops growing; if it is still growing at `MAX_ROUNDS` it REFUSES with the
last additions named.  A closure that stops at a guessed depth is a closure whose
answer depends on the guess.

WHAT IS STILL WRITTEN BY HAND, STATED PLAINLY
----------------------------------------------
The SEED set.  Everything reachable from the seeds is derived; the seeds
themselves are declared.  That residue is closed one notch by `unseeded_check()`:
every `a1wrt2_*` file in the item directory must be reachable from the seeds, so
an instrument that is written and never wired in is flagged rather than silently
omitted.  It is not closed all the way, and this docstring says so rather than
letting a reader assume it is.

NOTHING HERE IS FILED, SENT, UPLOADED, POSTED OR REGISTERED ANYWHERE.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ITEM = "A1WRT2"
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
ITEM_REL = str(HERE.relative_to(REPO))

# The SEEDS -- item-directory relative.  Declared, not derived; see the
# docstring's "WHAT IS STILL WRITTEN BY HAND".
SEEDS = ("a1wrt2_run_arm.sh", "a1wrt2_grade.py", "a1wrt2_stage.py",
         "a1wrt2_instruments.py")

MAX_ROUNDS = 24

# MODULES PROVIDED BY THE PINNED IMAGE AND BY NOTHING ON THIS HOST.
# `a1wr_runScript_incomp.py` imports `openmdao`, `mphys`, `dafoam` and `pygeo`.
# They are not in the repository and they are not installed on the box: they
# live inside `dafoam-idwarp-rot:v1`, `sha256:2927768a16ac...`, which is the
# image `a1wrt2_grade.PIN_IMG_DIGEST` pins.  Left undeclared, all four are
# reported ABSENT and the table cries wolf on every run; declared without a
# STATED LIMIT they become a hole through which a genuinely missing file could
# be excused.  So the declaration is narrow, named, and carries its limit here:
#
#   THIS LANE CANNOT VERIFY THAT THE IMAGE PROVIDES THEM.  Doing so means
#   starting the container, which is compute, and this item is not frozen.  The
#   four names below are therefore REPORTED, in their own third state, and are
#   NEVER counted as present.  `G-IMG` is what actually binds the image, at
#   launch, by digest.  The control `imports/undeclared-unresolvable-is-flagged`
#   plants an import that is neither in the tree nor on this list and asserts it
#   is still ABSENT, so the list cannot act as a blanket.
# `idwarp` joins the list on the same footing and for the same measured reason:
# `so2a_xg.py:129` imports it to read `libidwarp.so` back out of the image, and
# the image this family pins is literally `dafoam-idwarp-rot:v1`.  It is added
# because the SO2a control's first run reported it ABSENT beside the real
# finding -- a checker whose true positive arrives next to a false one gets read
# less carefully, which is how a real finding dies.
CONTAINER_MODULES = frozenset({"dafoam", "mphys", "openmdao", "pygeo",
                               "idwarp"})

# Variables whose value is a RUN ROOT rather than an item directory.  Detected
# from the assignment, never assumed: in `SO2a` `$BASE` is the run root, and in
# `A1WRT2` `$BASE` is the item directory.  A rule that hard-coded either name
# would be wrong about the other file, which is the same "written from memory"
# failure one layer down.
_RUNROOT_PREFIX = "/home/ubuntu/certonomous-runs/"

_RE_ASSIGN = re.compile(r'^\s*(?:export\s+)?([A-Za-z_]\w*)=(.+?)\s*$')
_RE_REF = re.compile(r'\$\{?([A-Za-z_]\w*)\}?(/[^\s"\';:|)&]*)?')
_RE_HEREDOC = re.compile(r"<<-?\s*'?([A-Za-z_]\w*)'?\s*$")
_RE_PY_C = re.compile(r'python3?\s+-c\s+(["\'])(.*?)\1', re.S)
_RE_PY_IMPORT = re.compile(r'^\s*(?:import|from)\s+([A-Za-z_]\w*)', re.M)


class Refuse(Exception):
    def __init__(self, token: str, message: str, code: int = 5):
        super().__init__(message)
        self.token = token
        self.code = code


def refuse(token: str, message: str, code: int = 5) -> None:
    raise Refuse(token, message, code)


# =============================================================================
# READERS.  A reader answers `exists` and `read` over ONE tree -- a git tree at
# the freeze commit, or a directory on disk.  The extraction is identical over
# both, which is what lets the SO2a control run against a 2026-08-28 tree and
# against HEAD with the same code.
# =============================================================================


class DiskReader:
    kind = "disk"

    def __init__(self, root: Path):
        self.root = Path(root)
        self.name = "disk:%s" % self.root

    def exists(self, rel: str) -> bool:
        return (self.root / rel).exists()

    def read(self, rel: str):
        p = self.root / rel
        if not p.is_file():
            return None
        return p.read_text(errors="replace")

    def listdir(self, rel: str):
        p = self.root / rel
        return sorted(x.name for x in p.iterdir()) if p.is_dir() else []

    def blob(self, rel: str):
        p = self.root / rel
        return p.read_bytes() if p.is_file() else None


class TreeReader:
    kind = "tree"

    def __init__(self, treeish: str, repo: Path):
        self.treeish = treeish
        self.repo = Path(repo)
        self.name = "tree:%s" % treeish
        out = subprocess.run(["git", "ls-tree", "-r", "--name-only", treeish],
                             cwd=str(self.repo), capture_output=True, text=True)
        if out.returncode != 0:
            refuse("TREE_UNREADABLE",
                   "cannot list tree %s: %s" % (treeish, out.stderr.strip()), 3)
        self.files = set(out.stdout.splitlines())
        self.dirs = set()
        for f in self.files:
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.dirs.add("/".join(parts[:i]))

    def exists(self, rel: str) -> bool:
        return rel in self.files or rel in self.dirs

    def read(self, rel: str):
        if rel not in self.files:
            return None
        out = subprocess.run(["git", "show", "%s:%s" % (self.treeish, rel)],
                             cwd=str(self.repo), capture_output=True)
        if out.returncode != 0:
            return None
        return out.stdout.decode("utf-8", "replace")

    def listdir(self, rel: str):
        pre = rel.rstrip("/") + "/"
        return sorted({f[len(pre):].split("/")[0]
                       for f in self.files if f.startswith(pre)})

    def blob(self, rel: str):
        if rel not in self.files:
            return None
        out = subprocess.run(["git", "show", "%s:%s" % (self.treeish, rel)],
                             cwd=str(self.repo), capture_output=True)
        return out.stdout if out.returncode == 0 else None


# =============================================================================
# EXTRACTION -- SHELL
# =============================================================================


def _strip_comment(line: str) -> str:
    out, q = [], None
    for ch in line:
        if q:
            out.append(ch)
            if ch == q:
                q = None
            continue
        if ch in "\"'":
            q = ch
            out.append(ch)
            continue
        if ch == "#" and (not out or out[-1] in " \t"):
            break
        out.append(ch)
    return "".join(out)


def shell_dir_vars(text: str, item_rel: str) -> dict:
    """Bind each shell variable to ITEM / REPO / RUNROOT / FILE, FROM ITS
    ASSIGNMENT.  `$BASE` is the run root in `so2a_chain_driver.sh` and the item
    directory in `a1wrt2_run_arm.sh`; a rule that assumed either would be wrong
    about the other."""
    env = {}
    for raw in text.splitlines():
        line = _strip_comment(raw)
        m = _RE_ASSIGN.match(line)
        if not m:
            continue
        name, rhs = m.group(1), m.group(2).strip()
        rhs = rhs.strip('"').strip("'")
        # `${VAR:-default}` -- the default is the binding that matters here
        d = re.match(r'^\$\{\w+:-(.*)\}$', rhs)
        if d:
            rhs = d.group(1)
        if "dirname" in rhs and ("BASH_SOURCE" in rhs or "$0" in rhs):
            env[name] = ("ITEM", "")
            continue
        if rhs.startswith(_RUNROOT_PREFIX):
            env[name] = ("RUNROOT", rhs[len(_RUNROOT_PREFIX):].split("/", 1)[1]
                         if "/" in rhs[len(_RUNROOT_PREFIX):] else "")
            continue
        if rhs.startswith(str(REPO) + "/"):
            env[name] = ("REPO", rhs[len(str(REPO)) + 1:])
            continue
        mv = re.match(r'^\$\{?(\w+)\}?(/.*)?$', rhs)
        if mv and mv.group(1) in env:
            kind, base = env[mv.group(1)]
            tail = (mv.group(2) or "").lstrip("/")
            env[name] = (kind, (base + "/" + tail).strip("/") if base else tail)
    return env


def _shell_python_fragments(text: str):
    """`python3 -c "..."` strings and `<<'TAG'` heredocs, returned as python
    source fragments.  `a1wrt2_run_arm.sh` imports `a1wrt2_grade` inside a
    `python3 -c` string, and an extractor that only read the shell would miss
    the single most important dependency in the file."""
    frags = [m.group(2) for m in _RE_PY_C.finditer(text)]
    lines, i = text.splitlines(), 0
    while i < len(lines):
        m = _RE_HEREDOC.search(_strip_comment(lines[i]))
        if m:
            tag, body, j = m.group(1), [], i + 1
            while j < len(lines) and lines[j].strip() != tag:
                body.append(lines[j])
                j += 1
            frags.append("\n".join(body))
            i = j
        i += 1
    return frags


def refs_from_shell(text: str, item_rel: str) -> tuple:
    """(static refs, dynamic refs) as (kind, relpath) pairs.

    The charter's own words: *every `$HERE/`, `$BASE/` and `$LAUNCHER`-style
    path reference*.  A tail carrying a further `$` is DYNAMIC -- reported so a
    reader can see it, never gated, because gating an interpolated name would
    make every launcher fail on its own `STATUS.$arm`."""
    env = shell_dir_vars(text, item_rel)
    static, dynamic = set(), set()
    for raw in text.splitlines():
        line = _strip_comment(raw)
        for m in _RE_REF.finditer(line):
            var, tail = m.group(1), m.group(2)
            if var not in env:
                continue
            kind, base = env[var]
            if tail is None:
                if kind == "FILE":
                    static.add((kind, base))
                continue
            t = tail.lstrip("/")
            if "$" in t:
                dynamic.add((kind, ((base + "/" + t.split("$")[0]).strip("/")
                                    if base else t.split("$")[0])))
                continue
            t = t.rstrip("/.,;")
            if not t:
                continue
            static.add((kind, (base + "/" + t).strip("/") if base else t))
    return static, dynamic


# =============================================================================
# EXTRACTION -- PYTHON
# =============================================================================


def _fold_paths(tree: ast.Module, item_rel: str) -> dict:
    """Module-level constants that name a DIRECTORY, folded.

    `HERE = Path(__file__).resolve().parent` -> the item directory;
    `REPO = HERE.parents[4]`                 -> the repository root;
    `FIXTURES = HERE / "fixtures"`           -> item/fixtures.
    Without this, `FIXTURES / "g_unbound_positive.sh"` is an unresolvable join
    and the nine committed fixtures would never enter the table."""
    env = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        val = _eval_path(node.value, env)
        if val is not None:
            env[node.targets[0].id] = val
    return env


def _eval_path(node, env):
    """Returns (kind, relpath) or None.  Deliberately tiny: it understands only
    the four shapes this family's instruments actually use."""
    if isinstance(node, ast.Call):
        f = node.func
        # Path(__file__).resolve().parent
        if isinstance(f, ast.Attribute) and f.attr == "resolve":
            return _eval_path(f.value, env)
        if (isinstance(f, ast.Name) and f.id == "Path" and node.args
                and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "__file__"):
            return ("ITEM", "__file__")
        if (isinstance(f, ast.Name) and f.id in ("Path", "str")
                and node.args and isinstance(node.args[0], ast.Constant)):
            return None
        return None
    if isinstance(node, ast.Attribute):
        if node.attr == "parent":
            base = _eval_path(node.value, env)
            if base and base[1] == "__file__":
                return ("ITEM", "")
            if base:
                return (base[0], str(Path(base[1]).parent)
                        if base[1] not in ("", ".") else base[1])
        return None
    if isinstance(node, ast.Subscript):
        # HERE.parents[N]
        v = node.value
        if isinstance(v, ast.Attribute) and v.attr == "parents":
            base = _eval_path(v.value, env)
            idx = node.slice
            if base and isinstance(idx, ast.Constant) and isinstance(idx.value, int):
                if base[0] == "ITEM" and base[1] == "":
                    up = idx.value + 1
                    parts = ITEM_REL.split("/")
                    if up >= len(parts):
                        return ("REPO", "")
                    return ("REPO", "/".join(parts[:len(parts) - up]))
        return None
    if isinstance(node, ast.Name):
        return env.get(node.id)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        base = _eval_path(node.left, env)
        if base is None or not isinstance(node.right, ast.Constant):
            return None
        if not isinstance(node.right.value, str):
            return None
        joined = (base[1] + "/" + node.right.value).strip("/") if base[1] \
            else node.right.value
        return (base[0], joined.strip("/"))
    return None


def _is_local_module(name: str) -> bool:
    """A module that is NOT the standard library and NOT installed anywhere
    else is a LOCAL import and therefore an instrument.  Resolved with the item
    directory removed from `sys.path`, so `a1wrt2_grade` counts even while it
    sits on disk beside this file, and `numpy` never does."""
    if name in getattr(sys, "stdlib_module_names", ()):
        return False
    saved = list(sys.path)
    try:
        sys.path = [p for p in sys.path
                    if p not in ("", str(HERE), os.getcwd())]
        try:
            return importlib.util.find_spec(name) is None
        except Exception:                                        # noqa: BLE001
            return True
    finally:
        sys.path = saved


def refs_from_python(text: str, item_rel: str) -> tuple:
    """(static item/repo refs, run-root refs, dynamic refs)."""
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        refuse("UNPARSEABLE",
               "a derived instrument does not parse as python: %s" % e, 3)
    env = _fold_paths(tree, item_rel)
    static, runroot, dynamic, container = set(), set(), set(), set()

    def _import(name):
        top = name.split(".")[0]
        if not _is_local_module(top):
            return
        if top in CONTAINER_MODULES:
            container.add(top)
            return
        static.add(("ITEM", top + ".py"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for al in node.names:
                _import(al.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                _import(node.module)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            got = _eval_path(node, env)
            if got and got[1] and got[1] != "__file__":
                static.add(got)
            elif got is None:
                base = node
                depth = 0
                while (isinstance(base, ast.BinOp)
                       and isinstance(base.op, ast.Div)):
                    base = base.left
                    depth += 1
                if isinstance(base, ast.Name) and base.id in ("root", "run_root"):
                    seg = []
                    n = node
                    while isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
                        if isinstance(n.right, ast.Constant) and isinstance(
                                n.right.value, str):
                            seg.insert(0, n.right.value)
                        else:
                            seg.insert(0, "$")
                        n = n.left
                    joined = "/".join(seg)
                    (dynamic if "$" in joined else runroot).add(
                        ("RUNROOT", joined))
    return static, runroot, dynamic, container


def literal_tuple(text: str, name: str):
    """A module-level tuple/list of string literals, read out of the AST.  Used
    for the stager's `PRODUCTS` / `STAGED_INPUTS` / `STAGED_CASE_DIRS`, so the
    completeness check binds to the file's own declarations rather than to a
    second copy of them living here."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name):
            try:
                v = ast.literal_eval(node.value)
            except Exception:                                    # noqa: BLE001
                return None
            return tuple(v)
    return None


# =============================================================================
# THE PRODUCER TRACE.  Draft section 11 item 1a, added by the
# dafoam-supervisor's 2026-09-04 section 11.1 amendment.
#
# WHAT IT ANSWERS, AND WHY EXISTENCE DID NOT ANSWER IT
# ----------------------------------------------------
# `assert_existence` asks whether every DERIVED INSTRUMENT is on disk.
# `completeness` asks whether every RUN-ROOT NAME the instruments reference is
# DECLARED by the stager.  Both passed clean on an item in which
# `MANIFEST.json` -- the sole input of the HARD gates `G-IMG` and `G-FREEZE` --
# was written at exactly one site in the whole item: `a1wrt2_grade.py:1390`,
# inside `_build_happy_root`, WHICH IS THE SELFTEST FIXTURE BUILDER.
#
# A declaration is not a producer.  `PRODUCTS` is a list of names the RUN MUST
# CREATE; reading it as evidence that something creates them is the exact
# confusion the amendment caught, so `PRODUCTS` IS DELIBERATELY EXCLUDED from
# the producer set below and the exclusion is printed rather than assumed.
#
# THE DISCRIMINATOR IS DERIVED, NOT LISTED.  A hand-written list of "fixture
# builder" function names would have the same failure mode as every other list
# written from memory (section 18.3).  Instead the module's own call graph is
# built from its AST and each write site is attributed to the entry point that
# can reach it:
#
#     reachable from `main`      -> GRADED PATH   -> a real producer
#     reachable ONLY from `selftest` -> FIXTURE   -> NOT a producer
#     reachable from neither     -> UNREACHED     -> reported, never a producer
#
# so moving a producer into a selftest-only helper is caught by construction,
# and a control drives exactly that move on a real tree.
#
# A HARD GATE FED BY NOTHING IS WORSE THAN A MISSING GATE, BECAUSE IT REPORTS.
# =============================================================================

# Path methods that WRITE, that READ, and that create a DIRECTORY.  Attribute
# names, matched on the call, so `(root / "x").write_text(...)` is a write and
# `(root / "x").read_text()` is a read without either being listed by name.
_WRITE_ATTRS = frozenset({"write_text", "write_bytes", "touch"})
_DIRWRITE_ATTRS = frozenset({"mkdir", "makedirs"})
_READ_ATTRS = frozenset({"read_text", "read_bytes", "exists", "is_file",
                         "is_dir", "stat", "iterdir", "glob", "rglob"})
# Module-level helpers whose FIRST argument is a path they READ.  Derived from
# the graders' own shape (`read_text(root / "ledger.txt")`); a name here that
# does not exist in the file is simply never matched, so the list cannot
# manufacture a trace.
_READ_FUNCS = frozenset({"read_text", "md5_of", "_iter_files"})

# The two entry points every instrument in this item has.  `main` is the graded
# path; `selftest` is the fixture path.  Named here because they are the CLI's
# own two entry points, and the control `producer/fixture-only-write-is-flagged`
# demonstrates that the distinction is what does the work.
_GRADED_ENTRIES = ("main",)
_FIXTURE_ENTRIES = ("selftest",)


def _runroot_rel(node):
    """A `root / "A" / "B"` chain -> `"A/B"`, or None.

    Rooted on the names this family's graders actually bind a run root to.  A
    segment that is not a string literal makes the whole reference DYNAMIC and
    returns None, so an interpolated name is never silently traced."""
    seg, n = [], node
    while isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
        if isinstance(n.right, ast.Constant) and isinstance(n.right.value, str):
            seg.insert(0, n.right.value)
        else:
            return None
        n = n.left
    if not (isinstance(n, ast.Name) and n.id in ("root", "run_root")):
        return None
    return "/".join(seg) if seg else None


def _toplevel_funcs(tree: ast.Module) -> dict:
    return {n.name: n for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _callgraph(funcs: dict) -> dict:
    """name -> set of top-level function names it calls.

    Nested `def`s and closures are attributed to their enclosing top-level
    function, which is what makes `_st_gate_controls`'s inner helpers land on
    the selftest side rather than nowhere."""
    names = set(funcs)
    cg = {}
    for fname, node in funcs.items():
        called = set()
        for x in ast.walk(node):
            if not isinstance(x, ast.Call):
                continue
            f = x.func
            if isinstance(f, ast.Name) and f.id in names:
                called.add(f.id)
            elif isinstance(f, ast.Attribute) and f.attr in names:
                called.add(f.attr)
        # a bare reference (passed as a callback, e.g. `_control("x", "fail", fn)`)
        # is a call for reachability purposes; missing this would strand every
        # leg that hands its body to `_control`
        for x in ast.walk(node):
            if isinstance(x, ast.Name) and x.id in names and x.id != fname:
                called.add(x.id)
        cg[fname] = called
    return cg


def _reachable(cg: dict, entries, stop=frozenset()) -> set:
    """Reachability with CUT NODES.

    ⚠ THE CUT IS LOAD-BEARING AND ITS ABSENCE WAS MEASURED, NOT REASONED.  The
    first drive of this trace against the real tree reported
    `MANIFEST.json  TRACED <- a1wrt2_grade.py:1390 in _build_happy_root
    [GRADED]` -- the exact artefact the section 11.1 amendment was written
    about, reported CLEAN.  The cause: every one of this item's instruments has
    `main` dispatch `--selftest` to `selftest()`, so an unstopped walk from
    `main` reaches every fixture builder and the graded/fixture discriminator
    collapses to "everything is graded".  A checker that cannot tell the two
    apart would have printed a clean trace over the defect it exists to find,
    which is `CLAUDE.md` rule 3 arriving one level up: a reader that has only
    ever reported "all traced" is not evidence.  The control
    `producer/fixture-only-write-is-flagged` pins the repaired behaviour."""
    seen, front = set(), [e for e in entries if e in cg]
    while front:
        cur = front.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur in stop:
            continue
        front.extend(cg.get(cur, ()))
    return seen


def runroot_io(text: str) -> dict:
    """Run-root READS and WRITES in one python instrument, each attributed to
    its enclosing top-level function and to that function's reachability.

    Returns {"read": {rel: [site]}, "write": {rel: [site]},
             "dirwrite": {rel: [site]}, "graded": set, "fixture": set,
             "unreached": set}, where a site is (function, lineno, path-role)."""
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        refuse("UNPARSEABLE",
               "a derived instrument does not parse as python: %s" % e, 3)
    funcs = _toplevel_funcs(tree)
    cg = _callgraph(funcs)
    # `selftest` is a CUT NODE on the graded walk: `main --selftest` dispatches
    # to it, and without the cut every fixture builder reads as graded.
    graded = _reachable(cg, _GRADED_ENTRIES,
                        stop=frozenset(_FIXTURE_ENTRIES)) \
        - set(_FIXTURE_ENTRIES)
    fixture = _reachable(cg, _FIXTURE_ENTRIES) - graded
    unreached = set(funcs) - graded - fixture

    owner = {}
    for fname, node in funcs.items():
        for x in ast.walk(node):
            owner[id(x)] = fname

    read, write, dirwrite = {}, {}, {}

    def role(fn):
        if fn in graded:
            return "GRADED"
        if fn in fixture:
            return "FIXTURE"
        return "UNREACHED"

    def add(bucket, rel, node):
        fn = owner.get(id(node), "<module>")
        bucket.setdefault(rel, []).append((fn, node.lineno, role(fn)))

    for x in ast.walk(tree):
        if not isinstance(x, ast.Call):
            continue
        f = x.func
        if isinstance(f, ast.Attribute):
            rel = _runroot_rel(f.value)
            if rel is None:
                continue
            if f.attr in _WRITE_ATTRS:
                add(write, rel, x)
            elif f.attr in _DIRWRITE_ATTRS:
                add(dirwrite, rel, x)
            elif f.attr in _READ_ATTRS:
                add(read, rel, x)
            continue
        if isinstance(f, ast.Name):
            if f.id == "open" and x.args:
                rel = _runroot_rel(x.args[0])
                if rel is None:
                    continue
                mode = ""
                if len(x.args) > 1 and isinstance(x.args[1], ast.Constant):
                    mode = str(x.args[1].value)
                add(write if any(c in mode for c in "wax") else read, rel, x)
            elif f.id in _READ_FUNCS and x.args:
                rel = _runroot_rel(x.args[0])
                if rel is not None:
                    add(read, rel, x)
    return {"read": read, "write": write, "dirwrite": dirwrite,
            "graded": graded, "fixture": fixture, "unreached": unreached}


_RE_REDIR = re.compile(r'(?:^|\s)(>>?)\s*("?)([^\s"\';|&)]+)\2')


def runroot_writes_shell(text: str, item_rel: str) -> dict:
    """Run-root WRITES in one shell instrument: every `>` / `>>` redirection
    whose target resolves under the run root, via the same variable binding the
    reference extractor uses.  A launcher that redirects the container's stdout
    into `$RUN_ROOT/$ARM/out/sweep.log` IS that log's producer, and this is what
    sees it."""
    env = shell_dir_vars(text, item_rel)
    out = {}
    for ln, raw in enumerate(text.splitlines(), 1):
        line = _strip_comment(raw)
        for m in _RE_REDIR.finditer(line):
            tok = m.group(3)
            mv = re.match(r'^\$\{?(\w+)\}?(/.*)?$', tok)
            if not mv or mv.group(1) not in env:
                continue
            kind, base = env[mv.group(1)]
            if kind != "RUNROOT":
                continue
            tail = (mv.group(2) or "").lstrip("/").rstrip("/.,;")
            rel = (base + "/" + tail).strip("/") if base else tail
            if not rel:
                continue
            role = "DYNAMIC" if "$" in rel else "GRADED"
            out.setdefault(rel, []).append(("<shell>", ln, role))
    return out


def deferred_producers(reader, item_rel: str):
    """The REGISTERED DEFERRAL REGISTRY, read out of the stager's AST.

    An entry is legal only if it NAMES what would produce the artefact and
    NAMES WHAT REFUSES IF IT IS ABSENT AT GRADE TIME.  A deferral without a
    refusal is a hole, so an entry missing either key is itself a finding."""
    text = reader.read(item_rel + "/a1wrt2_stage.py")
    if text is None:
        return None, []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None, []
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "DEFERRED_PRODUCERS"):
            try:
                val = ast.literal_eval(node.value)
            except Exception:                                    # noqa: BLE001
                return None, ["DEFERRED_PRODUCERS is not a literal"]
            bad = []
            for k, v in (val or {}).items():
                if not isinstance(v, dict):
                    bad.append("%s: not a mapping" % k)
                    continue
                for key in ("producer", "why_deferred", "refuses_if_absent"):
                    if not str(v.get(key, "")).strip():
                        bad.append("%s: missing %s" % (k, key))
            return val, bad
    return {}, []


def producer_trace(closure: dict, reader, item_rel: str) -> dict:
    """EVERY RUN-ROOT ARTEFACT A GATE READS ON THE GRADED PATH, TRACED TO A
    PRODUCER IN THE REGISTERED SET OR TO A NAMED REGISTERED DEFERRAL.

    Neither -> UNTRACED, and `main` returns non-zero on it.  A hard gate fed by
    nothing is worse than a missing gate, because it reports."""
    produced, fixture_only, consumed = {}, {}, {}
    unreached_writes = {}
    for path in sorted(closure["instruments"]):
        text = reader.read(path)
        if text is None:
            continue
        if path.endswith(".py"):
            io = runroot_io(text)
            for rel, sites in io["read"].items():
                for s in sites:
                    if s[2] == "GRADED":
                        consumed.setdefault(rel, []).append((path,) + s)
            for bucket in ("write", "dirwrite"):
                for rel, sites in io[bucket].items():
                    for s in sites:
                        tgt = (produced if s[2] == "GRADED"
                               else fixture_only if s[2] == "FIXTURE"
                               else unreached_writes)
                        tgt.setdefault(rel, []).append((path,) + s)
        elif path.endswith(".sh"):
            for rel, sites in runroot_writes_shell(text, item_rel).items():
                for s in sites:
                    (produced if s[2] == "GRADED"
                     else unreached_writes).setdefault(rel, []).append(
                        (path,) + s)

    # The stager's OWN declarations of what IT creates.  `STAGED_INPUTS` and
    # `STAGED_CASE_DIRS` are things the stager carries in or builds, so they are
    # producer evidence.  `PRODUCTS` IS NOT, AND THE EXCLUSION IS THE POINT:
    # it declares what the RUN must create, and reading it as a producer is
    # exactly the confusion the section 11.1 amendment caught.
    stager_text = reader.read(item_rel + "/a1wrt2_stage.py")
    staged = set()
    if stager_text is not None:
        for nm in ("STAGED_INPUTS", "STAGED_CASE_DIRS"):
            staged |= set(literal_tuple(stager_text, nm) or ())
    for rel in staged:
        produced.setdefault(rel, []).append(
            (item_rel + "/a1wrt2_stage.py", "<declared>", 0, "GRADED"))

    deferrals, deferral_defects = deferred_producers(reader, item_rel)

    traced, by_fixture, by_deferral, untraced = {}, {}, {}, {}
    for rel in sorted(consumed):
        if rel in produced:
            traced[rel] = produced[rel]
        elif deferrals and rel in deferrals:
            by_deferral[rel] = deferrals[rel]
        elif rel in fixture_only:
            by_fixture[rel] = fixture_only[rel]
        else:
            untraced[rel] = consumed[rel]
    return {"consumed": consumed, "produced": produced,
            "fixture_only": fixture_only, "unreached_writes": unreached_writes,
            "traced": traced, "by_deferral": by_deferral,
            "fixture_only_consumed": by_fixture, "untraced": untraced,
            "deferrals": deferrals, "deferral_defects": deferral_defects,
            "products_excluded": sorted(
                set(literal_tuple(stager_text, "PRODUCTS") or ())
                if stager_text is not None else ())}


# =============================================================================
# THE CLOSURE
# =============================================================================


def _to_repo(kind: str, rel: str, item_rel: str) -> str:
    return rel if kind == "REPO" else (item_rel + "/" + rel).strip("/")


def derive(seeds, reader, item_rel: str, max_rounds: int = MAX_ROUNDS) -> dict:
    """Transitive closure to a FIXED POINT, or a refusal.

    Returns {"instruments": {repo_rel: [why...]}, "runroot": set, "dynamic": set,
    "rounds": n}."""
    found = {}
    for s in seeds:
        found[_to_repo("ITEM", s, item_rel)] = ["SEED"]
    runroot, dynamic, container = set(), set(), set()
    frontier = list(found)
    rounds = 0
    while frontier:
        rounds += 1
        if rounds > max_rounds:
            refuse("NONCONVERGENT",
                   "the dependency closure was still growing after %d rounds; "
                   "last additions: %s.  A closure that stops at a guessed "
                   "depth is a closure whose answer depends on the guess, so "
                   "this refuses instead of truncating."
                   % (max_rounds, sorted(frontier)[:5]), 3)
        nxt = []
        for path in frontier:
            text = reader.read(path)
            if text is None:
                continue                       # absence is the existence pass's
            owner_rel = str(Path(path).parent)
            if path.endswith(".sh"):
                st, dy = refs_from_shell(text, item_rel)
                for frag in _shell_python_fragments(text):
                    for m in _RE_PY_IMPORT.finditer(frag):
                        nm = m.group(1)
                        if not _is_local_module(nm):
                            continue
                        if nm in CONTAINER_MODULES:
                            container.add(nm)
                        else:
                            st.add(("ITEM", nm + ".py"))
                rr = set()
            elif path.endswith(".py"):
                st, rr, dy, ct = refs_from_python(text, item_rel)
                container |= ct
            else:
                continue
            for kind, rel in st:
                if kind == "RUNROOT":
                    runroot.add(rel)
                    continue
                base = item_rel if kind == "ITEM" else ""
                # a reference inside a NON-item instrument resolves against ITS
                # own directory, which is how a dependency in a sibling item's
                # folder is reached at all
                if kind == "ITEM" and owner_rel not in (".", item_rel):
                    base = owner_rel
                tgt = (base + "/" + rel).strip("/") if base else rel
                tgt = os.path.normpath(tgt)
                if tgt not in found:
                    found[tgt] = []
                    nxt.append(tgt)
                found[tgt].append("from %s" % path)
            for _k, rel in rr:
                runroot.add(rel)
            for kind, rel in dy:
                dynamic.add("%s:%s" % (kind, rel))
        frontier = nxt
    return {"instruments": found, "runroot": runroot, "dynamic": dynamic,
            "container": container, "rounds": rounds}


class ExistenceTable:
    """Constructible ONLY by `assert_existence` returning clean.  `md5_table`
    takes one of these as its first argument, so no md5 in this file can be
    computed before existence has been asserted -- section 18.3's "existence
    first, and separately", made structural rather than conventional."""

    def __init__(self, reader, present: list, token: str):
        if token != "EXISTENCE-ASSERTED-CLEAN":
            refuse("EXISTENCE_TOKEN",
                   "an ExistenceTable was constructed without the existence "
                   "pass having returned clean", 3)
        self.reader = reader
        self.present = list(present)


def assert_existence(closure: dict, reader) -> tuple:
    """FIRST, AND SEPARATELY.  Returns (ExistenceTable|None, present, absent)."""
    present, absent = [], []
    for path in sorted(closure["instruments"]):
        (present if reader.exists(path) else absent).append(path)
    if absent:
        return None, present, absent
    return (ExistenceTable(reader, present, "EXISTENCE-ASSERTED-CLEAN"),
            present, absent)


def md5_table(tbl: ExistenceTable) -> dict:
    if not isinstance(tbl, ExistenceTable):
        refuse("MD5_BEFORE_EXISTENCE",
               "md5_table was called with something other than a clean "
               "ExistenceTable.  An md5-agreement figure is never evidence "
               "that the instrument set is COMPLETE (DAFOAM_CHARTER 18.3).", 3)
    out = {}
    for path in tbl.present:
        blob = tbl.reader.blob(path)
        # A DIRECTORY has no md5 and is reported as a directory rather than as
        # a null hash.  A null in an md5 column is exactly the cell a reader
        # skims past, and this table exists because a reader skimmed past one.
        out[path] = (hashlib.md5(blob).hexdigest() if blob is not None
                     else "(directory -- existence asserted, no md5)")
    return out


def unseeded_check(reader, item_rel: str, closure: dict, prefix: str) -> list:
    """Every `<prefix>*` file in the item directory must be REACHABLE from the
    seeds.  Closes one notch of the hand-written residue: an instrument written
    and never wired in is flagged, not silently omitted."""
    have = {p.split("/")[-1] for p in closure["instruments"]
            if p.startswith(item_rel + "/") and "/" not in p[len(item_rel) + 1:]}
    out = []
    for name in reader.listdir(item_rel):
        if name.startswith(prefix) and name.rsplit(".", 1)[-1] in ("py", "sh") \
                and name not in have:
            out.append(name)
    return sorted(out)


def completeness(closure: dict, reader, item_rel: str) -> tuple:
    """Every RUN-ROOT name the derived instruments reference must be covered by
    the stager's OWN declared lists, read out of the stager's AST.

    This is the same question one layer out: `G-DELIVERY` can read `OK 8` while
    the thing the code actually needs is missing.  Here the thing that would be
    missing is a run-root artefact the GRADER reads and the STAGER never makes,
    and the item would discover it after the compute rather than before it."""
    stager = item_rel + "/a1wrt2_stage.py"
    text = reader.read(stager)
    if text is None:
        # NOT a finding, and returning one here would be a false refusal: this
        # check runs over foreign items too (the SO2a historical control), and
        # those have no A1WRT2 stager to read declarations out of.  `None` means
        # NOT APPLICABLE and is printed as such; an empty list would read as
        # "checked, nothing found", which is the sentence rule 3 forbids.
        return None, None
    declared = set()
    for nm in ("PRODUCTS", "STAGED_INPUTS", "STAGED_CASE_DIRS"):
        vals = literal_tuple(text, nm)
        if vals:
            declared |= set(vals)
    uncovered = []
    for rel in sorted(closure["runroot"]):
        if rel in declared:
            continue
        # a declared name covers everything BELOW it (the staged case tree) and
        # every directory ABOVE it (declaring `TAIL/out/rc` declares `TAIL/out`
        # and `TAIL`); only a name on neither side is a real gap
        if any(rel.startswith(d + "/") or d.startswith(rel + "/")
               for d in declared):
            continue
        uncovered.append(rel)
    return declared, uncovered


# =============================================================================
# REPORT
# =============================================================================


def run_table(reader, item_rel: str, seeds, max_rounds=MAX_ROUNDS,
              do_md5=True) -> dict:
    cl = derive(seeds, reader, item_rel, max_rounds)
    tbl, present, absent = assert_existence(cl, reader)
    res = {"reader": reader.name, "rounds": cl["rounds"],
           "n_derived": len(cl["instruments"]),
           "present": present, "absent": absent,
           "container": sorted(cl["container"]),
           "runroot": sorted(cl["runroot"]), "dynamic": sorted(cl["dynamic"]),
           "why": {k: v for k, v in cl["instruments"].items()},
           "md5": None, "declared": None, "uncovered": None, "unseeded": None,
           "trace": None}
    if absent:
        # EXISTENCE FAILED.  No md5 is computed.  The `md5` field stays None and
        # a control asserts exactly that, because "we hashed everything and it
        # all agreed" is the sentence SO2a's freeze could truthfully print.
        return res
    if do_md5:
        res["md5"] = md5_table(tbl)
    dec, unc = completeness(cl, reader, item_rel)
    res["declared"], res["uncovered"] = (sorted(dec) if dec else None), unc
    res["unseeded"] = unseeded_check(reader, item_rel, cl, "a1wrt2_")
    res["trace"] = producer_trace(cl, reader, item_rel)
    return res


def print_table(res: dict) -> None:
    print("%s INSTRUMENT TABLE -- ENUMERATED BY EXTRACTION "
          "(DAFOAM_CHARTER 18.3)" % ITEM)
    print("reader: %s   closure rounds to fixed point: %d   derived: %d"
          % (res["reader"], res["rounds"], res["n_derived"]))
    print("")
    print("--- EXISTENCE, ASSERTED FIRST AND SEPARATELY ---")
    for p in res["present"]:
        print("  EXISTS  %s" % p)
    for p in res["absent"]:
        print("  ABSENT  %s   <-- the frozen code executes or imports this" % p)
    print("  %d present, %d ABSENT" % (len(res["present"]), len(res["absent"])))
    if res.get("container"):
        print("")
        print("--- IMPORTS PROVIDED BY THE PINNED IMAGE: REPORTED, NOT GATED,")
        print("    AND NEVER COUNTED AS PRESENT (unverifiable without compute) ---")
        for c in res["container"]:
            print("  IMAGE   %s   (dafoam-idwarp-rot:v1; bound at launch by "
                  "G-IMG, not here)" % c)
    if res["absent"]:
        print("")
        print("  NO MD5 WAS COMPUTED.  An md5-agreement figure over the files "
              "that ARE present would read as agreement while a dependency the "
              "frozen code executes is missing -- which is SO2a exactly.")
        return
    print("")
    print("--- MD5, COMPUTED ONLY AFTER EXISTENCE PASSED ---")
    for p, m in sorted((res["md5"] or {}).items()):
        print("  %s  %s" % (m, p))
    print("")
    if res["uncovered"] is None:
        print("--- RUN-ROOT NAMES: COVERAGE NOT APPLICABLE (no A1WRT2 stager "
              "in this item) ---")
        for r in res["runroot"]:
            print("  %-34s n/a" % r)
    else:
        print("--- RUN-ROOT NAMES THE INSTRUMENTS REFERENCE ---")
        for r in res["runroot"]:
            mark = "UNCOVERED <--" if r in res["uncovered"] else "covered"
            print("  %-34s %s" % (r, mark))
    if res["dynamic"]:
        print("")
        print("--- DYNAMIC REFERENCES: REPORTED, NOT GATED ---")
        for d in res["dynamic"]:
            print("  %s" % d)
    if res["unseeded"]:
        print("")
        print("--- ITEM FILES NOT REACHABLE FROM THE SEEDS ---")
        for u in res["unseeded"]:
            print("  UNSEEDED  %s" % u)
    if res.get("trace"):
        print_trace(res["trace"])


def _site(s) -> str:
    path, fn, ln, role = s
    return "%s:%s in %s [%s]" % (path.split("/")[-1], ln, fn, role)


def print_trace(t: dict) -> None:
    """Draft section 11 item 1a.  Every gate input traced to a producer, to a
    named registered deferral, or REFUSED."""
    print("")
    print("--- PRODUCER TRACE: every run-root artefact a gate READS on the")
    print("    GRADED path, traced to a PRODUCER in the registered set or to a")
    print("    NAMED REGISTERED DEFERRAL (draft section 11 item 1a) ---")
    if t["products_excluded"]:
        print("    `PRODUCTS` IS EXCLUDED FROM THE PRODUCER SET BY DESIGN: it")
        print("    declares what the RUN must create, not that anything creates")
        print("    it.  Reading it as a producer is the confusion the 11.1")
        print("    amendment caught.  Excluded: %s"
              % ", ".join(t["products_excluded"]))
    print("")
    for rel in sorted(t["consumed"]):
        if rel in t["traced"]:
            print("  TRACED    %-30s <- %s"
                  % (rel, "; ".join(_site(s) for s in t["traced"][rel][:2])))
        elif rel in t["by_deferral"]:
            d = t["by_deferral"][rel]
            print("  DEFERRED  %-30s producer: %s" % (rel, d.get("producer")))
            print("            refuses if absent at grade time: %s"
                  % d.get("refuses_if_absent"))
        elif rel in t["fixture_only_consumed"]:
            print("  UNTRACED  %-30s <-- WRITTEN ONLY BY THE SELFTEST FIXTURE "
                  "BUILDER" % rel)
            for s in t["fixture_only_consumed"][rel]:
                print("            fixture write at %s" % _site(s))
        else:
            print("  UNTRACED  %-30s <-- NOTHING IN THE REGISTERED SET WRITES "
                  "THIS" % rel)
            for s in t["untraced"][rel][:2]:
                print("            read at %s" % _site(s))
    n_bad = len(t["untraced"]) + len(t["fixture_only_consumed"])
    print("")
    print("  %d consumed, %d traced to a producer, %d covered by a registered "
          "deferral, %d UNTRACED"
          % (len(t["consumed"]), len(t["traced"]), len(t["by_deferral"]),
             n_bad))
    if t["deferral_defects"]:
        print("  DEFERRAL REGISTRY DEFECTS (a deferral without a refusal is a "
              "hole): %s" % t["deferral_defects"])
    if n_bad:
        print("  A HARD GATE FED BY NOTHING IS WORSE THAN A MISSING GATE, "
              "BECAUSE IT REPORTS.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A1WRT2 instrument table by "
                                             "extraction.  NOT FROZEN.")
    ap.add_argument("--tree", default=None,
                    help="git tree-ish to assert against (default: disk)")
    ap.add_argument("--item-dir", default=ITEM_REL)
    ap.add_argument("--seeds", default=",".join(SEEDS))
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()

    reader = TreeReader(a.tree, REPO) if a.tree else DiskReader(REPO)
    try:
        res = run_table(reader, a.item_dir,
                        tuple(s for s in a.seeds.split(",") if s))
    except Refuse as e:
        print("%s_INSTRUMENTS_REFUSED_%s rc=%d -- %s" % (ITEM, e.token, e.code, e))
        return e.code
    if a.json:
        print(json.dumps(res, indent=2, sort_keys=True, default=list))
    else:
        print_table(res)
    if res["absent"]:
        return 5
    if res["uncovered"]:
        print("")
        print("%s_INSTRUMENTS UNCOVERED RUN-ROOT NAMES: %s"
              % (ITEM, res["uncovered"]))
        return 6
    if res["unseeded"]:
        return 7
    # THE PRODUCER TRACE REFUSES.  An untraced gate input -- one nothing in the
    # registered set writes, or one written only by the selftest fixture builder
    # -- is a HARD GATE FED BY NOTHING, and this returns non-zero on it rather
    # than printing a table a reader would skim as clean.
    t = res.get("trace") or {}
    n_bad = len(t.get("untraced", {})) + len(t.get("fixture_only_consumed", {}))
    if t.get("deferral_defects"):
        print("")
        print("%s_INSTRUMENTS DEFERRAL REGISTRY DEFECTIVE: %s"
              % (ITEM, t["deferral_defects"]))
        return 9
    if n_bad:
        print("")
        print("%s_INSTRUMENTS UNTRACED GATE INPUTS: %s"
              % (ITEM, sorted(list(t["untraced"]) +
                              list(t["fixture_only_consumed"]))))
        return 8
    # CAP REACHABILITY, ordered by the dafoam-supervisor 2026-09-05.
    crc, cbody = cap_reachability()
    print("")
    print_cap_reachability(cbody)
    if crc:
        return crc
    return 0


# =============================================================================
# CAP REACHABILITY -- `w3s_stage_record.py:630`'s check, ported to this item by
# the `dafoam-supervisor`'s 2026-09-05 order: *"run `--cap-reachability`'s
# equivalent over EVERY `A1WRT2` leg before the freeze."*
#
# THE RULE, QUOTED FROM THE INSTRUMENT IT COMES FROM:
#     "cap x 60 / ranks < wall_bound, for every leg"
#
# ⚠ THE DIRECTION IS THE WHOLE CONTENT OF THE RULE AND IS EASY TO GET BACKWARDS
# -- THIS LANE GOT IT BACKWARDS ON 2026-09-05 AND THE CHECK IS WHAT CAUGHT IT.
# The cap must bind BEFORE the timeout.  A cap whose wall-equivalent is at or
# above its own in-container deadline is a DEAD LEVER: the timeout kills first,
# always, so the cap is a registered number no execution path can ever reach,
# and every sentence about "the cap stops the run" is false of it.  A cap BELOW
# its deadline is correct and healthy -- the cap stops the run, the deadline is
# the outer backstop for when the driver, the daemon and every agent are dead.
#
# EQUALITY IS NOT REACHABLE.  `<` is strict, deliberately: a cap that exactly
# equals its deadline cannot be shown to have bound first.
# =============================================================================

# Registered in draft section 5.4.  ranks = 1 is section 3's registered program.
CAP_LEGS = {
    "SEAM": {"cap_core_min": 10.0,  "ranks": 1, "deadline_s": 900},
    "TAIL": {"cap_core_min": 675.0, "ranks": 1, "deadline_s": 41400},
}
CAP_ITEM_CEILING = 685.0


def cap_reachability(legs=None, ceiling=None):
    """Returns (rc, body).  rc=0 only when EVERY registered cap is reachable
    AND the caps sum exactly to the registered ceiling.  rc=64 names every dead
    lever it found.  Takes its inputs as parameters so the control can plant a
    dead lever and be shown able to see one."""
    legs = CAP_LEGS if legs is None else legs
    ceiling = CAP_ITEM_CEILING if ceiling is None else ceiling
    rows, dead = [], []
    for name in sorted(legs):
        spec = legs[name]
        cap, ranks, bound = (spec["cap_core_min"], spec["ranks"],
                             spec["deadline_s"])
        cap_s = cap * 60.0 / float(ranks)
        ok = cap_s < bound
        rows.append({"leg": name, "cap_core_min": cap, "ranks": ranks,
                     "cap_wall_s": cap_s, "deadline_s": bound,
                     "reachable": ok,
                     "headroom_pct": (100.0 * (bound / cap_s - 1.0)
                                      if cap_s > 0 else None)})
        if not ok:
            dead.append(rows[-1])
    total = sum(l["cap_core_min"] for l in legs.values())
    sums = abs(total - ceiling) < 1e-9
    body = {"rule": "cap x 60 / ranks < deadline_s, for every leg",
            "legs": rows, "caps_sum_core_min": total,
            "item_ceiling_core_min": ceiling,
            "caps_sum_equals_ceiling": sums, "dead_levers": dead}
    if dead:
        body["verdict"] = "BLOCKED"
        body["reason"] = (
            "DEAD LEVER: %s.  A cap at or above its own timeout can never bind "
            "-- the timeout binds first, always -- so it is a registered number "
            "no execution path can reach.  THE ITEM DOES NOT FREEZE."
            % "; ".join(
                "leg %s caps at %.1f core-min = %.0f s against a %d s deadline"
                % (d["leg"], d["cap_core_min"], d["cap_wall_s"],
                   d["deadline_s"]) for d in dead))
        return 64, body
    if not sums:
        body["verdict"] = "BLOCKED"
        body["reason"] = (
            "REGISTRATION INCONSISTENT: the caps sum to %.3f, the registered "
            "ceiling is %.3f.  A registration whose parts do not equal its "
            "whole is a defect found here or not at all." % (total, ceiling))
        return 64, body
    body["verdict"] = "OK"
    return 0, body


def print_cap_reachability(body) -> None:
    print("--- CAP REACHABILITY (%s) ---" % body["rule"])
    for r in body["legs"]:
        print("  %-6s cap=%8.1f core-min  ranks=%d  cap_wall=%9.1f s  "
              "deadline=%7d s  %-11s headroom=%s"
              % (r["leg"], r["cap_core_min"], r["ranks"], r["cap_wall_s"],
                 r["deadline_s"],
                 "REACHABLE" if r["reachable"] else "DEAD LEVER",
                 ("%.1f %%" % r["headroom_pct"])
                 if r["headroom_pct"] is not None else "-"))
    print("  caps sum = %.3f core-min ; registered ceiling = %.3f ; equal = %s"
          % (body["caps_sum_core_min"], body["item_ceiling_core_min"],
             body["caps_sum_equals_ceiling"]))
    if body.get("reason"):
        print("  %s: %s" % (body["verdict"], body["reason"]))


# =============================================================================
# === SELFTEST BOUNDARY ===  ZERO `assert` statements anywhere in this file.
# =============================================================================

_CONTROL_LOG: list = []


def _control(name: str, expect: str, fn) -> None:
    state, detail = "NOT EXERCISED", ""
    try:
        detail = fn()
        state = "EXERCISED-FAIL" if expect == "fail" else "EXERCISED-PASS"
    except Refuse as e:
        state, detail = "NOT EXERCISED", "control itself refused: %s" % e
    except Exception as e:                                       # noqa: BLE001
        state, detail = "NOT EXERCISED", "control raised %s: %s" % (
            type(e).__name__, e)
    _CONTROL_LOG.append((name, expect, state, detail))
    print("CONTROL %-38s %-15s %s" % (name, state, detail))
    if state == "NOT EXERCISED":
        raise Refuse("CONTROL_NOT_EXERCISED",
                     "control %s did not reach its %s direction -- %s"
                     % (name, expect, detail), 1)


def _must(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


# ---- THE HISTORICAL PLANTED CONTROL, section 18.3's own worked instance -----
SO2A_ITEM = "cases/dafoam/ladder-a/A1/curriculum_SO2a"
SO2A_FREEZE = "5f0e083e"
SO2A_MISSING = SO2A_ITEM + "/so2a_aggregate_memory.py"


def _leg_so2a() -> None:
    """`DAFOAM_CHARTER.md` section 18.3 names the exact control this checker
    must be born on: it MUST flag `so2a_aggregate_memory.py` against the
    `5f0e083e` tree and MUST NOT flag it against HEAD.  A checker that has only
    ever reported "all present" is not evidence (`CLAUDE.md` rule 3, applied to
    the checker rather than to a comparator)."""

    def at_freeze():
        r = TreeReader(SO2A_FREEZE, REPO)
        res = run_table(r, SO2A_ITEM, ("so2a_chain_driver.sh",))
        _must(SO2A_MISSING in res["absent"],
              "the 5f0e083e tree did NOT flag %s; absent=%s"
              % (SO2A_MISSING, res["absent"]))
        _must(res["md5"] is None,
              "an md5 table was computed even though a dependency is ABSENT -- "
              "that is the SO2a ordering defect reproduced inside its own check")
        return ("5f0e083e -> ABSENT %d incl. so2a_aggregate_memory.py; md5 "
                "table NOT computed" % len(res["absent"]))

    _control("so2a/flags-the-missing-dep-at-freeze", "fail", at_freeze)

    def at_head():
        r = TreeReader("HEAD", REPO)
        res = run_table(r, SO2A_ITEM, ("so2a_chain_driver.sh",))
        _must(SO2A_MISSING not in res["absent"],
              "HEAD flagged %s, so the checker cannot tell the trees apart"
              % SO2A_MISSING)
        _must(SO2A_MISSING in res["present"],
              "%s is neither present nor absent at HEAD -- it was never derived,"
              " so the freeze-side flag would have been an accident"
              % SO2A_MISSING)
        return ("HEAD -> so2a_aggregate_memory.py DERIVED and PRESENT, "
                "not flagged")

    _control("so2a/does-not-flag-it-at-HEAD", "pass", at_head)


def _leg_a1wrt2() -> None:
    """The item's own table, on disk and at HEAD, plus the deliberate-removal
    control that shows the extractor able to report a non-zero on THIS item."""

    def on_disk():
        res = run_table(DiskReader(REPO), ITEM_REL, SEEDS)
        _must(not res["absent"], "ABSENT on disk: %s" % res["absent"])
        _must(res["n_derived"] >= 12,
              "only %d instruments derived -- the closure is not reaching the "
              "fixtures" % res["n_derived"])
        _must(res["md5"] is not None, "no md5 table after a clean existence pass")
        return ("%d derived in %d rounds, 0 ABSENT, %d md5s"
                % (res["n_derived"], res["rounds"], len(res["md5"])))

    _control("a1wrt2/table-on-disk", "pass", on_disk)

    def removal():
        """A DELIBERATELY REMOVED dependency, on a copy of the real item."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dst = root / ITEM_REL
            dst.parent.mkdir(parents=True)
            import shutil as _sh
            _sh.copytree(str(HERE), str(dst))
            # the producer lives in a SIBLING item's directory -- the shape SO2a
            # missed -- so removing THAT is the sharpest single test
            prod_rel = ("cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/"
                        "a1wr_runScript_incomp.py")
            (root / prod_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / prod_rel).write_text("# stand-in\n")
            r = DiskReader(root)
            base = run_table(r, ITEM_REL, SEEDS, do_md5=True)
            _must(not base["absent"],
                  "the control's own baseline is dirty: %s" % base["absent"])
            victim = ITEM_REL + "/fixtures/g_unbound_positive.sh"
            (root / victim).unlink()
            (root / prod_rel).unlink()
            after = run_table(r, ITEM_REL, SEEDS)
            _must(victim in after["absent"],
                  "the removed fixture was NOT flagged: %s" % after["absent"])
            _must(prod_rel in after["absent"],
                  "the removed SIBLING-ITEM producer was NOT flagged: %s"
                  % after["absent"])
            _must(after["md5"] is None,
                  "md5s were computed despite two ABSENT dependencies")
            return ("baseline 0 ABSENT -> after removal 2 ABSENT "
                    "(one fixture, one sibling-item producer), md5 NOT computed")

    _control("a1wrt2/deliberate-removal-is-seen", "fail", removal)

    def at_head():
        r = TreeReader("HEAD", REPO)
        res = run_table(r, ITEM_REL, SEEDS)
        return ("HEAD -> %d derived, %d ABSENT: %s"
                % (res["n_derived"], len(res["absent"]),
                   res["absent"] or "(none)"))

    _control("a1wrt2/table-at-HEAD", "pass", at_head)

    def undeclared():
        """`CONTAINER_MODULES` excuses four named imports the pinned image
        provides.  A list that excuses anything is a hole, so this plants an
        import that is neither in the tree nor on that list and asserts it is
        still reported ABSENT -- and asserts the four declared names stay in
        their own state rather than migrating into `present`."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dst = root / ITEM_REL
            dst.parent.mkdir(parents=True)
            import shutil as _sh
            _sh.copytree(str(HERE), str(dst))
            prod_rel = ("cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/"
                        "a1wr_runScript_incomp.py")
            (root / prod_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / prod_rel).write_text(
                "import openmdao.api as om\n"
                "from dafoam.mphys import DAFoamBuilder\n"
                "import a1wrt2_no_such_helper\n")
            r = DiskReader(root)
            res = run_table(r, ITEM_REL, SEEDS)
            want = ("cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/"
                    "a1wrt2_no_such_helper.py")
            _must(want in res["absent"],
                  "an undeclared unresolvable import was NOT flagged: %s"
                  % res["absent"])
            _must(set(res["container"]) >= {"openmdao", "dafoam"},
                  "the declared image modules were not reported: %s"
                  % res["container"])
            _must(not any(m in " ".join(res["present"])
                          for m in ("openmdao.py", "dafoam.py")),
                  "a declared image module was counted as PRESENT")
            return ("undeclared import -> ABSENT; openmdao/dafoam -> IMAGE "
                    "state, never counted present")

    _control("imports/undeclared-unresolvable-is-flagged", "fail", undeclared)


def _leg_ordering() -> None:
    """Existence BEFORE md5, and the ordering asserted structurally."""

    def cannot():
        try:
            md5_table("not a table")                     # type: ignore[arg-type]
        except Refuse as e:
            _must(e.token == "MD5_BEFORE_EXISTENCE", "wrong token %s" % e.token)
            return "md5_table refuses anything but a clean ExistenceTable"
        raise ValueError("md5_table accepted a non-table")

    _control("ordering/md5-refuses-without-existence", "fail", cannot)

    def forged():
        try:
            ExistenceTable(DiskReader(REPO), [], "I-SAY-SO")
        except Refuse as e:
            _must(e.token == "EXISTENCE_TOKEN", "wrong token %s" % e.token)
            return "an ExistenceTable cannot be forged with a different token"
        raise ValueError("a forged ExistenceTable was accepted")

    _control("ordering/existence-table-cannot-be-forged", "fail", forged)


def _leg_convergence() -> None:
    """A closure that has not converged REFUSES rather than guessing a depth."""

    def chain():
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            item = "cases/synthetic_chain"
            (root / item).mkdir(parents=True)
            n = 8
            for i in range(n):
                nxt = "link%d.sh" % (i + 1)
                (root / item / ("link%d.sh" % i)).write_text(
                    'HERE="$(cd "$(dirname "$0")" && pwd)"\n'
                    'bash "$HERE/%s"\n' % nxt)
            (root / item / ("link%d.sh" % n)).write_text("echo end\n")
            r = DiskReader(root)
            ok = run_table(r, item, ("link0.sh",), max_rounds=MAX_ROUNDS)
            _must(ok["n_derived"] == n + 1,
                  "the %d-link chain derived %d" % (n + 1, ok["n_derived"]))
            try:
                run_table(r, item, ("link0.sh",), max_rounds=3)
            except Refuse as e:
                _must(e.token == "NONCONVERGENT", "wrong token %s" % e.token)
                return ("a %d-link chain closes in %d rounds; capped at 3 it "
                        "REFUSES NONCONVERGENT rather than truncating"
                        % (n + 1, ok["rounds"]))
            raise ValueError("a truncated closure was returned as an answer")

    _control("convergence/refuses-rather-than-truncating", "fail", chain)


def _leg_completeness() -> None:
    """A run-root name no declaration covers is UNCOVERED."""

    def planted():
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dst = root / ITEM_REL
            dst.parent.mkdir(parents=True)
            import shutil as _sh
            _sh.copytree(str(HERE), str(dst))
            prod_rel = ("cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/"
                        "a1wr_runScript_incomp.py")
            (root / prod_rel).parent.mkdir(parents=True, exist_ok=True)
            (root / prod_rel).write_text("# stand-in\n")
            r = DiskReader(root)
            base = run_table(r, ITEM_REL, SEEDS)
            _must(not base["uncovered"],
                  "baseline already UNCOVERED: %s" % base["uncovered"])
            lp = dst / "a1wrt2_run_arm.sh"
            txt = lp.read_text()
            lp.write_text(txt.replace(
                'LEDGER="$RUN_ROOT/ledger.txt"',
                'LEDGER="$RUN_ROOT/ledger.txt"\n'
                'SNEAK="$RUN_ROOT/unregistered_thing.json"', 1))
            after = run_table(r, ITEM_REL, SEEDS)
            _must("unregistered_thing.json" in after["uncovered"],
                  "the planted run-root name was NOT flagged: %s"
                  % after["uncovered"])
            return ("baseline 0 UNCOVERED -> planted $RUN_ROOT/"
                    "unregistered_thing.json flagged UNCOVERED")

    _control("completeness/unregistered-runroot-name-flagged", "fail", planted)


def _leg_producer_trace() -> None:
    """THE PRODUCER TRACE, PLANTED BOTH WAYS ON REAL TREES.

    Draft section 11 item 1a.  An extractor that has only ever reported "all
    traced" is not evidence (`CLAUDE.md` rule 3), so every limb below is driven
    on a real copy of this item's own tree with one thing changed."""

    def _tree():
        """A real copy of the item tree plus the sibling item's frozen producer,
        under a temp repo root.  Same shape `_leg_completeness` uses."""
        import shutil as _sh
        td = tempfile.mkdtemp()
        root = Path(td)
        dst = root / ITEM_REL
        dst.parent.mkdir(parents=True)
        _sh.copytree(str(HERE), str(dst))
        prod_rel = ("cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/"
                    "a1wr_runScript_incomp.py")
        (root / prod_rel).parent.mkdir(parents=True, exist_ok=True)
        (root / prod_rel).write_text("# stand-in\n")
        return root, dst

    def baseline_is_clean():
        """THE PRESENT DIRECTION.  Every gate input on the real tree traces to
        a producer or to a named registered deferral, and NOTHING is untraced."""
        root, _dst = _tree()
        res = run_table(DiskReader(root), ITEM_REL, SEEDS, do_md5=False)
        t = res["trace"]
        _must(not t["untraced"] and not t["fixture_only_consumed"],
              "the real tree is NOT clean: untraced=%s fixture-only=%s"
              % (sorted(t["untraced"]), sorted(t["fixture_only_consumed"])))
        _must(t["by_deferral"],
              "no registered deferral was exercised, so the deferral branch is "
              "untested and 'all traced' could mean 'the branch never ran'")
        return ("%d gate inputs: %d traced to a producer, %d covered by a "
                "NAMED registered deferral, 0 untraced"
                % (len(t["consumed"]), len(t["traced"]), len(t["by_deferral"])))
    _control("producer/real-tree-traces-clean", "pass", baseline_is_clean)

    def removed_producer_refuses():
        """THE ABSENT DIRECTION.  The producer of `MANIFEST.json` -- the sole
        input of the HARD gates `G-IMG` and `G-FREEZE` -- is DELETED from the
        launcher on a real tree, and the trace must refuse."""
        root, dst = _tree()
        lp = dst / "a1wrt2_run_arm.sh"
        txt = lp.read_text()
        _must('> "$MANIFEST_PATH"' in txt or "$MANIFEST_PATH" in txt,
              "the launcher does not name MANIFEST_PATH, so this control is "
              "not removing what it thinks it is")
        lp.write_text(txt.replace('MANIFEST_PATH="$RUN_ROOT/MANIFEST.json"',
                                  'MANIFEST_PATH="/tmp/not_the_run_root.json"', 1))
        _must("/tmp/not_the_run_root.json" in lp.read_text(),
              "the mutation did not land on disk")
        res = run_table(DiskReader(root), ITEM_REL, SEEDS, do_md5=False)
        t = res["trace"]
        _must("MANIFEST.json" in t["untraced"]
              or "MANIFEST.json" in t["fixture_only_consumed"],
              "the producer of a HARD gate's only input was removed and the "
              "trace still reported it traced: untraced=%s fixture-only=%s"
              % (sorted(t["untraced"]), sorted(t["fixture_only_consumed"])))
        return ("MANIFEST_PATH repointed out of the run root -> MANIFEST.json "
                "flagged, and it is the ONLY input of the HARD gates G-IMG and "
                "G-FREEZE")
    _control("producer/removed-producer-is-flagged", "fail",
             removed_producer_refuses)

    def fixture_only_is_flagged():
        """THE SECTION 11.1 SHAPE ITSELF.  A producer MOVED OUT OF THE GRADED
        PATH INTO A SELFTEST-ONLY HELPER must be flagged FIXTURE-ONLY, not
        traced.  Existence and md5 agreement both read clean across this move,
        which is why neither of them caught it."""
        root, dst = _tree()
        lp = dst / "a1wrt2_run_arm.sh"
        lp.write_text(lp.read_text().replace(
            'MANIFEST_PATH="$RUN_ROOT/MANIFEST.json"',
            'MANIFEST_PATH="/tmp/not_the_run_root.json"', 1))
        gp = dst / "a1wrt2_grade.py"
        txt = gp.read_text()
        _must("_build_happy_root" in txt, "no fixture builder to point at")
        res = run_table(DiskReader(root), ITEM_REL, SEEDS, do_md5=False)
        t = res["trace"]
        _must("MANIFEST.json" in t["fixture_only_consumed"],
              "MANIFEST.json is written by `_build_happy_root` and by nothing "
              "on the graded path, yet the trace did not report it "
              "FIXTURE-ONLY: %s" % sorted(t["fixture_only_consumed"]))
        sites = t["fixture_only_consumed"]["MANIFEST.json"]
        _must(any(s[1] == "_build_happy_root" for s in sites),
              "the fixture site was not attributed to _build_happy_root: %s"
              % (sites,))
        return ("MANIFEST.json attributed to `_build_happy_root` [FIXTURE] and "
                "reported UNTRACED -- the section 11.1 defect, reproduced by "
                "extraction on a real tree")
    _control("producer/fixture-only-write-is-flagged", "fail",
             fixture_only_is_flagged)

    def cut_node_matters():
        """THE DISCRIMINATOR ITSELF, DRIVEN.  Without the `selftest` cut node,
        `main --selftest` reaches every fixture builder and the graded/fixture
        split collapses.  That is not a hypothesis: it is what the trace's FIRST
        run against the real tree actually printed, reporting
        `MANIFEST.json TRACED <- _build_happy_root [GRADED]`."""
        text = (HERE / "a1wrt2_grade.py").read_text()
        tree = ast.parse(text)
        cg = _callgraph(_toplevel_funcs(tree))
        uncut = _reachable(cg, _GRADED_ENTRIES)
        cut = _reachable(cg, _GRADED_ENTRIES,
                         stop=frozenset(_FIXTURE_ENTRIES))
        _must("_build_happy_root" in uncut,
              "the UNCUT walk does not reach the fixture builder, so this "
              "control is not demonstrating the collapse it claims")
        _must("_build_happy_root" not in cut,
              "the CUT walk still reaches the fixture builder -- the "
              "discriminator is not doing anything")
        return ("uncut walk from `main` reaches _build_happy_root (%d funcs); "
                "cut walk does not (%d funcs).  Without the cut the trace "
                "prints a clean table over the defect it exists to find"
                % (len(uncut), len(cut)))
    _control("producer/cut-node-is-load-bearing", "pass", cut_node_matters)

    def deferral_without_refusal_is_a_hole():
        """A DEFERRAL MISSING ITS `refuses_if_absent` IS ITSELF A FINDING."""
        root, dst = _tree()
        sp = dst / "a1wrt2_stage.py"
        txt = sp.read_text()
        _must('"refuses_if_absent"' in txt,
              "the registry does not carry a refuses_if_absent key to remove")
        sp.write_text(txt.replace('"refuses_if_absent":', '"_removed":', 1))
        _, defects = deferred_producers(DiskReader(root), ITEM_REL)
        _must(defects,
              "a deferral with NO refusal was accepted silently -- a deferral "
              "without a refusal is a hole with a name")
        return ("`refuses_if_absent` removed -> registry defect reported: %s"
                % defects)
    _control("producer/deferral-without-refusal-flagged", "fail",
             deferral_without_refusal_is_a_hole)

    def products_is_not_a_producer():
        """`PRODUCTS` DECLARES WHAT THE RUN MUST CREATE AND IS NOT EVIDENCE
        THAT ANYTHING CREATES IT.  Reading it as a producer is the exact
        confusion the section 11.1 amendment caught, so the exclusion is
        driven: every name in `PRODUCTS` is still required to trace on its own
        merits."""
        root, _dst = _tree()
        res = run_table(DiskReader(root), ITEM_REL, SEEDS, do_md5=False)
        t = res["trace"]
        _must(t["products_excluded"],
              "PRODUCTS was not read at all, so the exclusion is vacuous")
        overlap = [p for p in t["products_excluded"] if p in t["consumed"]]
        _must(overlap,
              "no PRODUCTS name is consumed by a gate, so this control proves "
              "nothing about the exclusion")
        for p in overlap:
            _must(p in t["traced"] or p in t["by_deferral"],
                  "%s is in PRODUCTS and is consumed by a gate, but traces to "
                  "neither a producer nor a deferral -- and PRODUCTS did not "
                  "rescue it, which is correct" % p)
        return ("%d PRODUCTS names excluded from the producer set; the %d of "
                "them a gate consumes each trace on their own merits"
                % (len(t["products_excluded"]), len(overlap)))
    _control("producer/PRODUCTS-is-not-a-producer", "pass",
             products_is_not_a_producer)


def _leg_noassert() -> None:
    def audit():
        for f in (Path(__file__), HERE / "a1wrt2_stage.py",
                  HERE / "a1wrt2_grade.py"):
            src = f.read_text(errors="replace")
            n = len([x for x in ast.walk(ast.parse(src))
                     if isinstance(x, ast.Assert)])
            _must(n == 0, "%s carries %d assert statements" % (f.name, n))
        planted = ast.parse("def _p():\n    assert 1 == 1\n")
        m = len([x for x in ast.walk(planted) if isinstance(x, ast.Assert)])
        _must(m == 1, "the auditor cannot see a planted assert")
        return ("ast.Assert = 0 in a1wrt2_instruments.py, a1wrt2_stage.py and "
                "a1wrt2_grade.py; auditor sees 1 when one is planted")

    _control("noassert/zero-across-the-three-instruments", "pass", audit)


def _leg_cap_reachability() -> None:
    """The `dafoam-supervisor`'s 2026-09-05 order, driven in BOTH directions.

    ⚠ THIS LEG EXISTS BECAUSE THE LANE THAT WROTE IT GOT THE RULE BACKWARDS.
    It reported `SEAM`'s 900 s deadline as a defect against a 10.0 core-min cap
    -- reasoning that a deadline above the cap cannot enforce it -- and edited
    the launcher to 600 s.  Driving the REAL rule from `w3s_stage_record.py:630`
    inverted the finding: 600 s makes `SEAM` a DEAD LEVER (cap_wall 600 s == a
    600 s deadline, and `<` is strict), while the registered 900 s is REACHABLE
    with 50 % headroom.  The edit was reverted.  **The genuine dead lever is
    `TAIL`**, whose 675.0 core-min cap WAS exactly its 40,500 s deadline.
    A check beats an argument, which is the entire reason the order was given.

    RESOLVED 2026-09-05: the supervisor RULED `TAIL`'s in-container deadline
    40,500 -> 41,400 s (cap x 1.02), so the REGISTERED CAP CAN ACTUALLY BIND and
    the deadline is a real backstop behind it.  That RAISES A BACKSTOP so an
    existing cap becomes enforceable: it moves no gate, no band and no
    threshold, and it is not a widening toward a pass -- a deadline sitting
    exactly at the cap is what made the cap unenforceable.  The 40,500 tie is
    pinned by `cap-reach/tail-tie-is-caught` so the state this item was
    registered in until 2026-09-05 cannot return unnoticed.

    ⚠ HEADROOM IS REPORTED AS A FRACTION OF THE CAP, NOT OF THE DEADLINE, and
    the two differ enough to matter in a record: SEAM reads **50.0 %** here
    (900/600 - 1) where the same gap is 33.3 % if taken over the deadline
    ((900-600)/900).  This file uses `w3s_stage_record.py`'s definition, so the
    two items' figures are comparable.  Stated because one number under two
    conventions is how a record acquires a contradiction nobody planted."""

    def registered_is_read():
        rc, body = cap_reachability()
        rows = {r["leg"]: r for r in body["legs"]}
        _must(rows["SEAM"]["cap_wall_s"] == 600.0,
              "SEAM cap_wall_s %r" % rows["SEAM"]["cap_wall_s"])
        _must(rows["TAIL"]["cap_wall_s"] == 40500.0,
              "TAIL cap_wall_s %r" % rows["TAIL"]["cap_wall_s"])
        _must(rows["SEAM"]["reachable"] is True, "SEAM should be REACHABLE")
        _must(rows["TAIL"]["reachable"] is True, "TAIL should be REACHABLE")
        _must(rc == 0, "the registered table must now return 0, got %r" % rc)
        _must(body["caps_sum_equals_ceiling"] is True, "caps must sum to 685.0")
        return ("SEAM 600.0 s wall vs a 900 s deadline -> REACHABLE (%.1f %% "
                "headroom); TAIL 40500.0 s wall vs the RULED 41400 s deadline "
                "-> REACHABLE (%.1f %% headroom); caps sum 685.000 == ceiling. "
                "rc=0" % (rows["SEAM"]["headroom_pct"],
                          rows["TAIL"]["headroom_pct"]))

    def tail_tie_is_caught():
        """The DEFECT AS REGISTERED UNTIL 2026-09-05, pinned so it cannot come
        back.  TAIL's deadline WAS exactly its cap's wall-equivalent."""
        legs = {"SEAM": {"cap_core_min": 10.0, "ranks": 1, "deadline_s": 900},
                "TAIL": {"cap_core_min": 675.0, "ranks": 1,
                         "deadline_s": 40500}}
        rc, body = cap_reachability(legs, 685.0)
        _must(rc == 64, "the 40500 tie must be caught, got rc %r" % rc)
        _must([d["leg"] for d in body["dead_levers"]] == ["TAIL"],
              "TAIL alone should be dead, got %r" % body["dead_levers"])
        return ("TAIL's ORIGINAL 40500 s deadline replayed: cap_wall 40500.0 s "
                "== deadline 40500 s -> DEAD LEVER, rc=64.  This is the state "
                "the item was registered in until the 2026-09-05 ruling, and "
                "it is pinned here so it cannot return unnoticed")

    def healthy_tree_is_clean():
        legs = {"SEAM": {"cap_core_min": 10.0, "ranks": 1, "deadline_s": 901},
                "TAIL": {"cap_core_min": 675.0, "ranks": 1,
                         "deadline_s": 40501}}
        rc, body = cap_reachability(legs, 685.0)
        _must(rc == 0, "a healthy table must return 0, got %r" % rc)
        _must(not body["dead_levers"], "no dead levers expected")
        return ("a MINIMAL healthy table -- each deadline ONE SECOND above its "
                "cap's wall-equivalent -- returns rc=0 and 0 dead levers.  One "
                "second is the whole difference, which is what `<` being "
                "strict means, and it shows the checker is not a function that "
                "refuses everything")

    def my_own_inverted_edit_is_caught():
        legs = {"SEAM": {"cap_core_min": 10.0, "ranks": 1, "deadline_s": 600},
                "TAIL": {"cap_core_min": 675.0, "ranks": 1,
                         "deadline_s": 40501}}
        rc, body = cap_reachability(legs, 685.0)
        _must(rc == 64, "the 600 s edit must be caught, got rc %r" % rc)
        _must([d["leg"] for d in body["dead_levers"]] == ["SEAM"],
              "SEAM alone should be dead, got %r" % body["dead_levers"])
        return ("the lane's own 900->600 edit, replayed: SEAM becomes the DEAD "
                "LEVER it was edited to avoid being.  The reverted edit is "
                "pinned by a control so it cannot be made again silently")

    def sum_mismatch_is_caught():
        legs = {"SEAM": {"cap_core_min": 10.0, "ranks": 1, "deadline_s": 900},
                "TAIL": {"cap_core_min": 674.0, "ranks": 1,
                         "deadline_s": 40501}}
        rc, body = cap_reachability(legs, 685.0)
        _must(rc == 64, "a caps/ceiling mismatch must refuse, got %r" % rc)
        _must(body["caps_sum_equals_ceiling"] is False, "should not sum")
        return ("caps summing to 684.0 against a registered 685.0 ceiling "
                "REFUSES: a registration whose parts do not equal its whole")

    _control("cap-reach/registered-table-is-read", "pass", registered_is_read)
    _control("cap-reach/tail-tie-is-caught", "fail", tail_tie_is_caught)
    _control("cap-reach/healthy-table-is-clean", "pass", healthy_tree_is_clean)
    _control("cap-reach/inverted-edit-is-caught", "fail",
             my_own_inverted_edit_is_caught)
    _control("cap-reach/caps-must-sum-to-ceiling", "fail", sum_mismatch_is_caught)


def selftest() -> int:
    print("%s_INSTRUMENTS SELFTEST -- host python, NO compute, NOT FROZEN" % ITEM)
    print("python %s   optimisation flag active: %s"
          % (sys.version.split()[0],
             "-O (asserts disabled)" if not __debug__ else "none"))
    legs = (("SELFTEST-SO2A-HISTORICAL-CONTROL", _leg_so2a),
            ("SELFTEST-A1WRT2-TABLE", _leg_a1wrt2),
            ("SELFTEST-ORDERING", _leg_ordering),
            ("SELFTEST-CONVERGENCE", _leg_convergence),
            ("SELFTEST-COMPLETENESS", _leg_completeness),
            ("SELFTEST-PRODUCER-TRACE", _leg_producer_trace),
            ("SELFTEST-CAP-REACHABILITY", _leg_cap_reachability),
            ("SELFTEST-NOASSERT", _leg_noassert))
    try:
        for name, fn in legs:
            print("")
            print("---- %s ----" % name)
            fn()
    except (Refuse, ValueError) as e:
        print("%s_INSTRUMENTS_SELFTEST FAILED -- %s" % (ITEM, e))
        return 1
    n_fail = len([c for c in _CONTROL_LOG if c[2] == "EXERCISED-FAIL"])
    n_pass = len([c for c in _CONTROL_LOG if c[2] == "EXERCISED-PASS"])
    n_not = len([c for c in _CONTROL_LOG if c[2] == "NOT EXERCISED"])
    print("")
    print("%s_INSTRUMENTS_SELFTEST legs=%d controls=%d EXERCISED-FAIL=%d "
          "EXERCISED-PASS=%d NOT-EXERCISED=%d"
          % (ITEM, len(legs), len(_CONTROL_LOG), n_fail, n_pass, n_not))
    if n_not:
        print("%s_INSTRUMENTS_SELFTEST REFUSED -- NOT EXERCISED is never a pass"
              % ITEM)
        return 1
    print("%s_INSTRUMENTS_SELFTEST OK -- the extractor is shown able to report "
          "a NON-ZERO, on real history and on this item's own bytes" % ITEM)
    return 0


if __name__ == "__main__":
    sys.exit(main())
