"""CENSUS v2 -- SELECTION OF ONE PATH FROM MANY BY ORDER RATHER THAN BY ROLE.

KEYED ON THE SHAPE, NOT ON A NAME LIST, so it enumerates a class instead of sampling it.

⚠ WHY AST AND NOT grep, MEASURED RATHER THAN ASSERTED.  The real shape spans lines:
    files = sorted((d / "probesBase").rglob("p"))     # the glob
    ...
    parse(files[-1].read_text())                      # the pick, 3 lines later
A single-line grep over this exact tree returned 4 hits -- ALL comments or a control's own
reproduction of old code -- and MISSED the two live sites feeding GRADED quantities.  A
LINE-ORIENTED KEY REPORTS A CLEAN ZERO OVER LIVE DEFECTS.

WHAT COUNTS AS THE SHAPE (bounded by construction, not by a list of names):
  a set of paths produced by glob/rglob/iterdir/listdir, possibly via sorted(), reduced to
  ONE path by ORDERING -- subscript [n]/[-n], max(), min(), or next(iter(...)).
BINDINGS ARE FOLLOWED TRANSITIVELY: a name derived from a globbed name (a comprehension, a
slice, a sorted() of it) still carries the shape.  ⚠ v1 followed ONE level and would have
missed a derived binding; the seeded plant below contains that case so the gap cannot recur
silently.
ALL SCOPES ARE WALKED, module level included.  ⚠ v1 visited only FunctionDef and was blind
to module-level selection; the plant contains that case too.

THE PLANT IS A SEEDED FILE, NOT HARD-CODED LINE NUMBERS.  The census is handed a fixture
containing known instances -- including the two shapes v1 was blind to -- AND known
NON-instances, and must find exactly the former and none of the latter.  A CENSUS NOT SHOWN
ABLE TO FIND ONE IT WAS HANDED HAS NOT MEASURED ABSENCE.
"""
import ast
import sys
import tempfile
from pathlib import Path

GLOBBERS = {"glob", "rglob", "iterdir", "listdir"}
ORDERING_FUNCS = {"max", "min"}

PLANT_SRC = '''
from pathlib import Path

# SEEDED POSITIVE 1 -- module level (v1 was blind to this scope)
mod_files = sorted(Path("x").rglob("*.dat"))
mod_pick = mod_files[-1]


def seeded_positive_2_derived(d):
    """the index is on a name DERIVED from the globbed name (v1 was blind to this)"""
    found = sorted(Path(d).rglob("*.dat"))
    subset = [p for p in found if p.name]
    return subset[-1]


def seeded_positive_3_crossline(d):
    files = sorted(Path(d).rglob("*.dat"))
    return files[-1]


def seeded_positive_4_direct(d):
    return sorted(Path(d).rglob("*.dat"))[0]


def seeded_positive_5_max(d):
    return max(Path(d).glob("*.dat"))


def seeded_negative_1_no_index(d):
    """a glob that is ITERATED, never reduced to one by order -- NOT the shape"""
    total = 0
    for p in sorted(Path(d).rglob("*.dat")):
        total += p.stat().st_size
    return total


def seeded_negative_2_guarded_len(d):
    """indexed ONLY after the set is proved to hold exactly one -- NOT a defect, but the
    census still REPORTS it, because whether a guard is adequate is a JUDGEMENT and a
    census that silently swallows guarded sites is deciding instead of enumerating"""
    found = sorted(Path(d).rglob("*.dat"))
    if len(found) != 1:
        raise RuntimeError("ambiguous")
    return found[0]


def seeded_negative_3_not_a_glob(d):
    """an index over a plain list -- NOT the shape"""
    items = sorted([1, 2, 3])
    return items[-1]
'''

PLANT_EXPECT_FN = {
    "<module>", "seeded_positive_2_derived", "seeded_positive_3_crossline",
    "seeded_positive_4_direct", "seeded_positive_5_max", "seeded_negative_2_guarded_len",
}
PLANT_EXPECT_ABSENT = {"seeded_negative_1_no_index", "seeded_negative_3_not_a_glob"}

# ⚠ A SCOPE-LEAK CHECK, ADDED BECAUSE THE PLANT ABOVE DID NOT CATCH A REAL BUG.
# v2's first run reported EVERY function-scope site a SECOND time under `<module>`, and the
# plant passed anyway -- because its one module-level instance was genuine, so `<module>`
# appearing in the results looked correct.  A PLANT THAT ONLY CHECKS *WHETHER* A SCOPE
# APPEARS CANNOT SEE A SCOPE APPEARING FOR THE WRONG REASON.  This counts instead: the
# fixture has exactly ONE module-level site, so more than one is a leak.
PLANT_EXPECT_MODULE_COUNT = 1


# =====================================================================================
# THE REGISTERED CLASSIFICATION.  Kept HERE, in code, rather than in prose, so that
# re-running the census RE-CHECKS the classification instead of merely reprinting it: a
# site that appears and is not classified below is reported as UNCLASSIFIED and the census
# refuses.  THAT IS WHAT MAKES THE TWO SETS SUM -- a member with no reason beside it is
# skipped, not censused.
#
# AXIS 1 -- ROLE-SELECTABLE (a real "latest"/"only" exists; repair = order by that role) or
#           AMBIGUOUS (nothing orders them; repair = REFUSE).  Measured per site.
# AXIS 2 -- GRADED (the value reaches record.json and a campaign gate) or DIAGNOSTIC.
# =====================================================================================
# ⚠ KEYED ON (file, FUNCTION, KIND) AND NOT ON A LINE NUMBER, AND THAT IS A REPAIR OF THIS
# FILE'S OWN FIRST VERSION.  v2 keyed the table on (file, line).  Applying the very fix this
# census exists to enable MOVED THE LINES, and the census immediately reported five sites as
# UNCLASSIFIED that it had classified minutes earlier -- L-492 ("a line number alone is not a
# citation") committed by the tool built to enumerate a defect class.  A KEY THAT BREAKS WHEN
# THE FILE IS EDITED IS USELESS IN A TOOL WHOSE PURPOSE IS TO GUIDE EDITS.
CLASSIFICATION: dict[tuple[str, str, str], tuple[str, str, str]] = {
    ("cylinder_ladder.py", "base_cpb", "name-index:files"): (
        # ⚠ REPAIRED BY GAP 5(d). This entry no longer matches any site and is kept
        # as the record of what was found. Its absence from the output IS the repair.
        "AFFECTED", "ROLE-SELECTABLE / GRADED",
        "base_cpb(): files[-1] over probesBase.rglob('p'). Layout is probesBase/<time>/p, "
        "so a real latest EXISTS and the repair is numeric ordering, not refusal -- the "
        "yPlus shape, not the coefficient shape. GRADED: produces cpb_magnitude, which "
        "reaches record.json and which the campaign names among its gates "
        "(F5a_cylinder_reynolds_ladder.md:1139, 'gates (Cd, -Cpb, Cl_rms)'). LATENT, NOT "
        "REALISED: all 11 trees carry exactly one probe file, at time dir 0."),
    ("cylinder_ladder.py", "recirculation_length", "name-index:files"): (
        # ⚠ REPAIRED BY GAP 5(d). This entry no longer matches any site and is kept
        # as the record of what was found. Its absence from the output IS the repair.
        "AFFECTED", "ROLE-SELECTABLE / GRADED",
        "recirculation_length(): files[-1] over probesCenterline.rglob('U'). Same layout "
        "and same repair. GRADED, AND THE MOST SEVERE OF THE SEVEN: produces lr_over_d, "
        "which the campaign calls THIS LADDER'S PRIMARY GATE at Re 1000/2000/3900 "
        "(F5a_cylinder_reynolds_ladder.md:968). LATENT, NOT REALISED, on the same "
        "measurement."),
    ("cylinder_ladder.py", "_coefficient_series_path", "name-index:found"): (
        "NOT AFFECTED", "GUARDED",
        "_coefficient_series_path(): `return found[0]` runs ONLY after len(found) > 1 has "
        "raised. With exactly one candidate an index selects nothing -- no ordering "
        "decides a measurement. Reported rather than suppressed, because whether a guard "
        "is adequate is a JUDGEMENT and a census that silently swallows guarded sites is "
        "deciding instead of enumerating."),
    ("cylinder_ladder.py", "_latest_time_series_path", "max:"): (
        "NOT AFFECTED", "THIS IS THE REPAIR",
        "_yplus_series_path(): max(_time_key(p) for p in found) orders by the PARSED TIME, "
        "not by path text. The census flags max()-over-a-globbed-set by shape, correctly; "
        "the classification is that the ordering key is a number parsed from the directory "
        "name, which is the defect's repair and not the defect."),
    ("cylinder_ladder.py", "_latest_time_series_path", "name-index:at_latest"): (
        "NOT AFFECTED", "GUARDED",
        "_yplus_series_path(): `return at_latest[0]` runs ONLY after len(at_latest) > 1 "
        "has raised. Same reasoning as :708."),
    ("cylinder_ladder.py", "selftest_yplus_selection", "direct-index:"): (
        "NOT AFFECTED", "DELIBERATE REPRODUCTION OF THE OLD BEHAVIOUR",
        "selftest_yplus_selection(): the control's own sorted(...)[-1], present so the "
        "limb can assert that the OLD code picks t=5 while the new selector picks t=10. "
        "REMOVING IT WOULD WEAKEN THE TEST -- it is what makes that limb unable to pass "
        "vacuously."),
    ("cylinder_ladder.py", "selftest_series_selection", "direct-index:"): (
        "NOT AFFECTED", "DELIBERATE REPRODUCTION OF THE OLD BEHAVIOUR",
        "selftest_series_selection(): the generalised selector's control reproduces the old "
        "sorted(...)[-1] so its NUMERIC ORDER limb can assert that the old code picks t=5 "
        "while the new selector picks t=10. Added BY gap 5(d) itself -- and the census "
        "correctly reported it UNCLASSIFIED on the first run after the repair, which is the "
        "table doing its job rather than a gap in it."),
    ("run_rung.py", "selftest_harvest_delegation", "direct-index:"): (
        "NOT AFFECTED", "DELIBERATE REPRODUCTION OF THE OLD BEHAVIOUR",
        "selftest_harvest_delegation(): same, for the delegated yPlus selector."),
}


class Scanner(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hits: list[tuple[int, str, str]] = []
        self._scope: list[str] = ["<module>"]

    # ---- shape predicates -------------------------------------------------
    @staticmethod
    def _is_glob_call(n: ast.AST) -> bool:
        return (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in GLOBBERS)

    def _carries_shape(self, n: ast.AST, bound: dict[str, int]) -> bool:
        """Does this expression carry a SET OF GLOBBED PATHS (directly or derived)?"""
        if self._is_glob_call(n):
            return True
        if isinstance(n, ast.Name):
            return n.id in bound
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Name) and f.id in {"sorted", "list", "reversed", "tuple"}:
                return bool(n.args) and self._carries_shape(n.args[0], bound)
            return False
        if isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
            return any(self._carries_shape(g.iter, bound) for g in n.generators)
        if isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Slice):
            return self._carries_shape(n.value, bound)   # a slice keeps the set
        return False

    # ---- scope walk -------------------------------------------------------
    def _scan_scope(self, body: list[ast.stmt], name: str) -> None:
        bound: dict[str, int] = {}
        # fixed point: a derived binding may appear before its source is registered
        for _ in range(4):
            for n in self._iter_own(body):
                if isinstance(n, ast.Assign) and self._carries_shape(n.value, bound):
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            bound.setdefault(t.id, n.lineno)
        for n in self._iter_own(body):
            why = None
            if isinstance(n, ast.Subscript) and not isinstance(n.slice, ast.Slice):
                if self._carries_shape(n.value, bound):
                    if isinstance(n.value, ast.Name):
                        why = f"name-index:{n.value.id}"
                    else:
                        why = "direct-index:"
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                if n.func.id in ORDERING_FUNCS and n.args and self._carries_shape(
                        n.args[0], bound):
                    why = f"{n.func.id}:"
                elif n.func.id == "next" and n.args and isinstance(n.args[0], ast.Call):
                    inner = n.args[0]
                    if (isinstance(inner.func, ast.Name) and inner.func.id == "iter"
                            and inner.args and self._carries_shape(inner.args[0], bound)):
                        why = "next-iter:"
            if why:
                self.hits.append((n.lineno, name, why))

    @staticmethod
    def _iter_own(body: list[ast.stmt]):
        """Walk THIS SCOPE ONLY.

        ⚠ THE OBVIOUS VERSION OF THIS IS WRONG AND WAS WRONG HERE.  Testing the CHILD's
        type before descending is not enough: the children of a FunctionDef are ordinary
        statements, so the walk skipped the `def` and then happily descended into its body
        one level down.  Every function-scope site was reported a second time under
        `<module>`, and the module scope's binding table was polluted with names from
        inside functions.  THE TEST MUST BE ON THE NODE BEING VISITED, NOT ON ITS CHILDREN.
        """
        nested = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        stack = list(body)
        while stack:
            n = stack.pop()
            if isinstance(n, nested):
                continue                      # a different scope entirely -- do not enter
            yield n
            stack.extend(ast.iter_child_nodes(n))

    def run(self, tree: ast.Module) -> None:
        self._scan_scope(tree.body, "<module>")
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._scan_scope(n.body, n.name)


def scan(path: Path) -> list[tuple[int, str, str]]:
    s = Scanner()
    s.run(ast.parse(path.read_text()))
    return sorted(set(s.hits))


def plant() -> bool:
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "plant.py"
        p.write_text(PLANT_SRC)
        hits = scan(p)
    fns = {fn for _, fn, _ in hits}
    missing = PLANT_EXPECT_FN - fns
    false_pos = PLANT_EXPECT_ABSENT & fns
    print(f"  PLANT: seeded {len(PLANT_EXPECT_FN)} instances of the shape (including the "
          f"two v1 was blind to) and {len(PLANT_EXPECT_ABSENT)} non-instances.")
    print(f"    found        : {sorted(fns)}")
    if missing:
        print(f"    ⚠ MISSED     : {sorted(missing)}")
    if false_pos:
        print(f"    ⚠ FALSE ALARM: {sorted(false_pos)}")
    mod_count = sum(1 for _, fn, _ in hits if fn == "<module>")
    leaked = mod_count != PLANT_EXPECT_MODULE_COUNT
    if leaked:
        print(f"    ⚠ SCOPE LEAK: {mod_count} module-level sites reported, fixture has "
              f"exactly {PLANT_EXPECT_MODULE_COUNT} -- function bodies are being counted "
              "as module scope")
    else:
        print(f"    SCOPE: exactly {mod_count} module-level site, as seeded -- no leak "
              "from function bodies into module scope")
    ok = not missing and not false_pos and not leaked
    print("    DISCRIMINATES: every seeded instance found AND every seeded non-instance "
          f"left alone AND no scope leak = {ok}")
    return ok


def main(argv: list[str]) -> int:
    if not plant():
        print("\n  PLANT FAILED -- CENSUS REFUSED. A census not shown able to find an "
              "instance it was handed cannot certify absence anywhere.")
        return 2
    print()
    affected: list[str] = []
    clean: list[str] = []
    unclassified: list[str] = []
    total = 0
    files = 0
    for a in argv:
        p = Path(a)
        hits = scan(p)
        if not hits:
            continue
        files += 1
        for ln, fn, why in hits:
            total += 1
            key = (p.name, fn, why)
            row = CLASSIFICATION.get(key)
            label = f"{p.name}:{ln} {fn}()  [{why}]"
            if row is None:
                unclassified.append(f"{label} -- {why}")
                continue
            verdict, axes, reason = row
            entry = f"{label}\n        [{axes}] {reason}"
            (affected if verdict == "AFFECTED" else clean).append(entry)

    print(f"  AFFECTED ({len(affected)}):")
    for e in affected:
        print(f"    - {e}")
    print(f"\n  NOT AFFECTED ({len(clean)}), each with its reason:")
    for e in clean:
        print(f"    - {e}")
    if unclassified:
        print(f"\n  ⚠ UNCLASSIFIED ({len(unclassified)}) -- A MEMBER WITH NO REASON BESIDE "
              "IT IS SKIPPED, NOT CENSUSED:")
        for e in unclassified:
            print(f"    - {e}")

    print(f"\n  DO THE SETS SUM? {len(affected)} affected + {len(clean)} not affected "
          f"+ {len(unclassified)} unclassified = {len(affected)+len(clean)+len(unclassified)}"
          f", against {total} sites enumerated -- "
          f"{'YES' if len(affected)+len(clean)+len(unclassified) == total else 'NO'}")
    print(f"  Scanned {len(argv)} file(s); {files} carried at least one site.")
    if unclassified:
        print("\n  CENSUS INCOMPLETE: classify every member before acting on it.")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
