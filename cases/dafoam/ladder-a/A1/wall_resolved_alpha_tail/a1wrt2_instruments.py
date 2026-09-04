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
           "md5": None, "declared": None, "uncovered": None, "unseeded": None}
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
    return 0


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
