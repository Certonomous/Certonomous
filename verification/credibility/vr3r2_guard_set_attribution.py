#!/usr/bin/env python3
"""VR3-R2 -- are the ansys cardinality-guarded sites safe FOR THE REASON CLAIMED?

Gate: verification/campaign/VR3R2_PREREGISTRATION.md.

WHY A SECOND REGISTRATION EXISTS.  VR3's PASS was withdrawn to NOT A RESULT for
two defects, both in the predecessor and neither repairable in it (rule 6 --
frozen files are never edited):

  (a) POPULATION MISMATCH.  VR3_PREREGISTRATION.md:19 registered a gate over
      "each of the 11 sites" -- ansys's cardinality-guarded SAFE set less
      grade_vmfl076.  vr3_guard_set_attribution.py:62-72 instead walked EVERY
      grade_*.py in the tree and totalled 60 wildcard-bound reads (16 guarded,
      44 unguarded).  A different quantity over a different population.  How
      many of the registered sites are unguarded was never measured.

  (b) UNREACHABLE FAILING VERDICT.  vr3_guard_set_attribution.py:76-79 is the
      whole of its branching: the ONLY non-PASS return is both-totals-zero.
      The string "GATE FAIL" does not occur in that file.  It collects an
      `unguarded` list at :72 and never reads it.  The registered failing
      verdict was unreachable in the implementation, so its PASS carried no
      information -- it could not have come out any other way.

This driver does not import, execute or edit the frozen VR3 driver.

WHAT IS MEASURED.  Per registered site: G1 the ordered set that decides the
answer; G2 the set each len() guard actually measures; G3 whether they are the
same set; G4 the class.  The discriminator is SCOPE AND DOMINANCE, not the mere
presence of the name in a len() comparison somewhere in the module -- crediting
a guard in one function with the safety of a binding in another is the exact
defect DEAD_LEVER_AUDIT §7.4 found in ansys's own classifier.
"""
import ast
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REGISTRATION = "verification/campaign/VR3R2_PREREGISTRATION.md"
ANSYS = "cases/ansys_verification"

# ---------------------------------------------------------------------------
# THE REGISTERED POPULATION.  Frozen in VR3R2_PREREGISTRATION.md §2.
#
# It is a RECONSTRUCTION, not a transcription: ansys's "12 cardinality-guarded
# SAFE" is a bare count at docs/LAB_STATE.md@c7176346 with no enumeration
# anywhere in the repository.  The reconstruction predicate is stated in the
# registration and is validated against the one enumerated half that does
# exist -- the 19 hazard sites, which it reproduces 19/19 by file and line.
# On the guarded half it returns 14, of which the 2 grade_vmfl076.py sites are
# excluded by the registration, leaving the 12 below.  The residual 14-vs-12
# disagreement with ansys's count is DISCLOSED, not reconciled; see the
# registration.
#
# (path relative to the repo root, binding line, bound name)
# ---------------------------------------------------------------------------
POPULATION = [
    ("cases/ansys_verification/VMFL001/grade_vmfl001.py", 360, "hits"),
    ("cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py", 236, "hits"),
    ("cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py", 420, "hits"),
    ("cases/ansys_verification/VMFL005/grade_vmfl005.py", 152, "hits"),
    ("cases/ansys_verification/VMFL019/grade_vmfl019.py", 99, "hits"),
    ("cases/ansys_verification/VMFL050/grade_vmfl050.py", 118, "hits"),
    ("cases/ansys_verification/VMFL050/grade_vmfl050.py", 126, "hits"),
    ("cases/ansys_verification/VMFLGPU001/grade_vmflgpu001.py", 249, "hits"),
    ("cases/ansys_verification/VMFLGPU001/grade_vmflgpu001.py", 589, "hits"),
    ("cases/ansys_verification/VMFLGPU001-R2/grade_vmflgpu001_r2.py", 274, "hits"),
    ("cases/ansys_verification/VMFLGPU001-R2/grade_vmflgpu001_r2.py", 614, "hits"),
    ("cases/ansys_verification/VMFLGPU002/grade_vmflgpu002.py", 278, "hits"),
]

WILDCARD = "*?["


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------
def _name(n):
    if isinstance(n, ast.Attribute):
        return _name(n.value) + "." + n.attr
    if isinstance(n, ast.Name):
        return n.id
    return ""


def _numeric_key(call):
    """sorted(..., key=float|int) or sorted(<float(...) comprehension>)."""
    for kw in getattr(call, "keywords", []):
        if kw.arg == "key" and _name(kw.value) in ("float", "int"):
            return True
    if call.args:
        a = call.args[0]
        if isinstance(a, (ast.GeneratorExp, ast.ListComp)):
            e = a.elt
            if isinstance(e, ast.Call) and _name(e.func) in ("float", "int"):
                return True
    return False


class _Module:
    """One parsed grader.  Everything the per-site classifier needs."""

    def __init__(self, path, src):
        self.path = path
        self.tree = ast.parse(src)
        self.strbinds = {}      # name -> [str literals]  (module-wide, in order)
        self.bindings = []      # (name, lineno, kind, pattern)
        self.guards = []        # (name, lineno, text, has_literal_one)
        self.subs = []          # (name, lineno)
        self.funcs = []         # (lineno, end_lineno, qualname)
        self._walk(self.tree, [])

    def _strs(self, node):
        out = [n.value for n in ast.walk(node)
               if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id in self.strbinds:
                out.extend(self.strbinds[n.id])
        return out

    def _walk(self, node, stack):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                q = ".".join(stack + [child.name])
                self.funcs.append((child.lineno, child.end_lineno, q))
                self._walk(child, stack + [child.name])
                continue
            if isinstance(child, ast.ClassDef):
                self._walk(child, stack + [child.name])
                continue
            self._inspect(child)
            self._walk(child, stack)

    def _inspect(self, node):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
           and isinstance(node.targets[0], ast.Name):
            tgt = node.targets[0].id
            strs = self._strs(node.value)
            if strs:
                self.strbinds[tgt] = strs
            if isinstance(node.value, ast.Call):
                fn = _name(node.value.func)
                inner = ""
                if fn == "sorted" and node.value.args \
                   and isinstance(node.value.args[0], ast.Call):
                    inner = _name(node.value.args[0].func)
                if fn == "sorted" and inner in ("glob.glob", "os.listdir"):
                    kind = "NUMERIC" if _numeric_key(node.value) else "LEXICAL"
                    self.bindings.append(
                        (tgt, node.lineno, "%s:sorted(%s)" % (kind, inner), strs))
                elif fn in ("glob.glob", "os.listdir"):
                    self.bindings.append(
                        (tgt, node.lineno, "UNORDERED:%s" % fn, strs))
        if isinstance(node, ast.Compare):
            ones = any(isinstance(c, ast.Constant) and c.value == 1
                       for c in [node.left] + list(node.comparators))
            for side in [node.left] + list(node.comparators):
                if isinstance(side, ast.Call) and _name(side.func) == "len" \
                   and side.args and isinstance(side.args[0], ast.Name):
                    try:
                        txt = ast.unparse(node)
                    except Exception:
                        txt = "len(%s) <cmp>" % side.args[0].id
                    self.guards.append((side.args[0].id, node.lineno, txt, ones))
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            self.subs.append((node.value.id, node.lineno))

    def enclosing(self, line):
        """Innermost function containing `line`; (0, 10**9, '<module>') if none."""
        best = (0, 10 ** 9, "<module>")
        for lo, hi, q in self.funcs:
            if lo <= line <= hi and (hi - lo) < (best[1] - best[0]):
                best = (lo, hi, q)
        return best


def pattern_of(strs):
    return "/".join(s for s in strs if s) or "<no literal>"


def has_wildcard(strs):
    return any(ch in s for s in strs for ch in WILDCARD)


# ---------------------------------------------------------------------------
# THE PRODUCTION CLASSIFIER.  Both control limbs are driven through THIS
# function and through verdict() below -- never through a copy (§2p.3(d)).
# ---------------------------------------------------------------------------
def classify_site(path, line, name, src=None):
    """G1/G2/G3/G4 for one registered site.  Returns a dict, or None if the
    registered binding is not present at that line (caller must treat that as
    NOT A RESULT, never as a skip)."""
    if src is None:
        with open(path, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    m = _Module(path, src)

    here = [b for b in m.bindings if b[0] == name and b[1] == line]
    if not here:
        return None
    _, _, kind, strs = here[0]
    lo, hi, fq = m.enclosing(line)

    # G1 -- the ordered set that decides the answer.
    g1 = pattern_of(strs)

    # Every len(<name>) guard in the module, split by whether it can possibly
    # be measuring THIS binding's set.
    attributed, foreign = [], []
    rebinds = sorted(b[1] for b in m.bindings
                     if b[0] == name and lo <= b[1] <= hi and b[1] > line)
    next_rebind = rebinds[0] if rebinds else 10 ** 9
    for gname, gline, gtext, ones in m.guards:
        if gname != name:
            continue
        in_scope = lo <= gline <= hi
        dominates = line < gline < next_rebind
        if in_scope and dominates:
            attributed.append((gline, gtext, ones))
        else:
            # G2 -- WHICH set does this guard actually measure?  The set bound
            # to the same name nearest above the guard.
            prior = [b for b in m.bindings if b[0] == name and b[1] <= gline]
            prior.sort(key=lambda b: b[1])
            src_b = prior[-1] if prior else None
            foreign.append((gline, gtext, m.enclosing(gline)[2],
                            (src_b[1] if src_b else None),
                            (pattern_of(src_b[3]) if src_b else "<unbound>")))

    uses = sorted(l for n, l in m.subs if n == name and lo <= l <= hi and l > line)
    first_use = uses[0] if uses else None
    effective = [a for a in attributed
                 if a[2] and (first_use is None or a[0] <= first_use)]

    if kind.startswith("NUMERIC"):
        cls = "REFERENCE"
    elif effective:
        cls = "GUARDED"
    else:
        cls = "UNGUARDED"

    return dict(
        path=path, line=line, name=name, func=fq, kind=kind,
        g1=g1, wildcard=has_wildcard(strs),
        g2_attributed=attributed, g2_foreign=foreign,
        g3_same_set=bool(effective), first_use=first_use, cls=cls)


def verdict(rows, missing, population_size):
    """PRODUCTION verdict.  Returns (label, rc).

    Reachability of GATE FAIL is proved, not asserted: the negative control
    limb below drives a planted UNGUARDED site through classify_site and then
    through THIS function, and requires ('GATE FAIL', 1) back.
    """
    if population_size == 0:
        return ("NOT A RESULT", 2)          # §2p.2 empty-input arm
    if missing:
        return ("NOT A RESULT", 2)
    if not rows:
        return ("NOT A RESULT", 2)
    if any(r["cls"] == "UNGUARDED" for r in rows):
        return ("GATE FAIL", 1)
    return ("PASS", 0)


# ---------------------------------------------------------------------------
# PLANTED CONTROLS -- CLAUDE.md rule 3 / VERIFICATION §2p.3(e), BOTH LIMBS.
# A refuser that refuses everything is indistinguishable from a correct one,
# so the positive limb is as load-bearing as the negative one.  Both run in
# the SAME invocation that produces the verdict and their outcome is printed
# beside it.
# ---------------------------------------------------------------------------
_NEG = '''\
import glob, os

def reads_the_hard_input(level_dir):
    pat  = os.path.join(level_dir, "postProcessing", "probes", "*", "U")
    hits = sorted(glob.glob(pat))
    return hits[-1]

def a_different_function(level_dir):
    hits = sorted(glob.glob(os.path.join(level_dir, "pp", "*", "g.xy")))
    if len(hits) != 1:
        raise SystemExit(1)
    return hits[0]
'''

_POS = '''\
import glob, os

def reads_the_hard_input(level_dir):
    pat  = os.path.join(level_dir, "postProcessing", "probes", "*", "U")
    hits = sorted(glob.glob(pat))
    if len(hits) != 1:
        raise SystemExit(1)
    return hits[0]
'''


def _plant(src):
    fh = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
    fh.write(src)
    fh.close()
    return fh.name


def controls():
    """Drive both limbs through classify_site() and verdict().  Returns
    (all_ok, lines_to_print)."""
    out, ok = [], True

    # --- NEGATIVE / planted: an UNGUARDED wildcard-bound ordered read whose
    #     only len() guard lives in a DIFFERENT function over a DIFFERENT set.
    p = _plant(_NEG)
    try:
        r = classify_site(p, 5, "hits")
        got_cls = r["cls"] if r else "<site not found>"
        v = verdict([r] if r else [], [], 1)
        lim = (got_cls == "UNGUARDED" and v == ("GATE FAIL", 1))
        ok &= lim
        out.append("  %s NEGATIVE limb: planted unguarded site -> class=%s verdict=%s rc=%d"
                   % ("ok  " if lim else "FAIL", got_cls, v[0], v[1]))
        if r:
            out.append("       G2 foreign guards seen: %s"
                       % ([(g[0], g[1], "in %s over %s" % (g[2], g[4])) for g in r["g2_foreign"]] or "none"))
    finally:
        os.unlink(p)

    # --- POSITIVE: a site that DESERVES a pass -- the guard measures the very
    #     set the subscript reduces.  Must NOT be called UNGUARDED.
    p = _plant(_POS)
    try:
        r = classify_site(p, 5, "hits")
        got_cls = r["cls"] if r else "<site not found>"
        v = verdict([r] if r else [], [], 1)
        lim = (got_cls == "GUARDED" and v == ("PASS", 0))
        ok &= lim
        out.append("  %s POSITIVE limb: planted guarded site   -> class=%s verdict=%s rc=%d"
                   % ("ok  " if lim else "FAIL", got_cls, v[0], v[1]))
    finally:
        os.unlink(p)

    # --- §2p.2 EMPTY-INPUT ARM: an empty population must REFUSE, not report clean.
    v = verdict([], [], 0)
    lim = (v == ("NOT A RESULT", 2))
    ok &= lim
    out.append("  %s EMPTY-INPUT arm: empty population         -> verdict=%s rc=%d"
               % ("ok  " if lim else "FAIL", v[0], v[1]))

    # --- ABSENT-SITE arm: a registered site not present at HEAD must be
    #     NOT A RESULT, never silently skipped.
    p = _plant(_POS)
    try:
        r = classify_site(p, 999, "hits")
        v = verdict([], [(p, 999, "hits")], 1)
        lim = (r is None and v == ("NOT A RESULT", 2))
        ok &= lim
        out.append("  %s ABSENT-SITE arm: registered site gone   -> located=%s verdict=%s rc=%d"
                   % ("ok  " if lim else "FAIL", r is not None, v[0], v[1]))
    finally:
        os.unlink(p)

    return ok, out


# ---------------------------------------------------------------------------
# Registration-freeze check (rule 2 / SUPERVISION §3 check 4).  The graded
# measurement refuses to run against a registration that is not committed at
# HEAD, or whose working copy differs from the committed blob.
# ---------------------------------------------------------------------------
def registration_frozen():
    path = os.path.join(REPO, REGISTRATION)
    if not os.path.exists(path):
        return False, "registration absent from the working tree"
    try:
        head = subprocess.check_output(
            ["git", "-C", REPO, "rev-parse", "HEAD:" + REGISTRATION],
            stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return False, "registration is NOT COMMITTED at HEAD"
    disk = subprocess.check_output(
        ["git", "-C", REPO, "hash-object", path]).decode().strip()
    if disk != head:
        return False, ("working copy %s differs from committed blob %s"
                       % (disk[:12], head[:12]))
    return True, head


def main(argv):
    only_controls = "--controls" in argv

    print("VR3-R2 -- guard-set attribution over the REGISTERED population")
    print("Gate: %s" % REGISTRATION)
    print()
    print("CONTROLS (driven through the production classify_site()/verdict(), same run):")
    ok, lines = controls()
    for l in lines:
        print(l)
    print("  CONTROLS: %s" % ("PASS" if ok else "FAIL"))
    print()
    if not ok:
        print("VERDICT: NOT A RESULT -- the instrument failed its own controls; "
              "no number below it is evidence")
        return 2
    if only_controls:
        print("--controls: stopping before the graded measurement, by request.")
        return 0

    frozen, why = registration_frozen()
    if not frozen:
        print("VERDICT: NOT A RESULT -- %s. A gate is only a gate if it was "
              "frozen before the measurement (rule 2)." % why)
        return 2
    print("Registration frozen at blob %s" % why[:12])
    print()

    rows, missing = [], []
    for rel, line, name in POPULATION:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            missing.append((rel, line, name, "file absent at HEAD"))
            continue
        r = classify_site(p, line, name)
        if r is None:
            missing.append((rel, line, name, "no such binding at that line"))
            continue
        r["rel"] = rel
        rows.append(r)

    print("PER-SITE CLASSIFICATION (population registered N=%d):" % len(POPULATION))
    for r in rows:
        print("  %s:%d  %s  in %s" % (r["rel"].split("ansys_verification/")[-1],
                                      r["line"], r["name"], r["func"]))
        print("    G1 deciding set   : %s   [%s, wildcard=%s]"
              % (r["g1"], r["kind"], r["wildcard"]))
        if r["g2_attributed"]:
            print("    G2 guard measures : %s"
                  % "; ".join("line %d: %s%s" % (g[0], g[1],
                                                 "" if g[2] else "  (no literal 1 -- not a cardinality refusal)")
                              for g in r["g2_attributed"]))
        else:
            print("    G2 guard measures : NO len(%s) guard in %s after line %d"
                  % (r["name"], r["func"], r["line"]))
        for g in r["g2_foreign"]:
            print("    G2 foreign guard  : line %d %s -- in %s, over the set bound at line %s (%s)"
                  % (g[0], g[1], g[2], g[3], g[4]))
        print("    G3 same set?      : %s" % ("YES" if r["g3_same_set"] else "NO"))
        print("    G4 class          : %s" % r["cls"])
    for rel, line, name, why in missing:
        print("  %s:%d  %s  -- MISSING: %s"
              % (rel.split("ansys_verification/")[-1], line, name, why))

    label, rc = verdict(rows, missing, len(POPULATION))
    n_ung = sum(1 for r in rows if r["cls"] == "UNGUARDED")
    print()
    print("Classified %d of %d registered sites; UNGUARDED=%d GUARDED=%d REFERENCE=%d; missing=%d"
          % (len(rows), len(POPULATION), n_ung,
             sum(1 for r in rows if r["cls"] == "GUARDED"),
             sum(1 for r in rows if r["cls"] == "REFERENCE"), len(missing)))
    print("CONTROLS: PASS (negative limb proved the GATE FAIL branch reachable "
          "in this same run)")
    print("VERDICT: %s" % label)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
