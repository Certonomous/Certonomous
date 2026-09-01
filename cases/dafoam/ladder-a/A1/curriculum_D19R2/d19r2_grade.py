#!/usr/bin/env python3
"""CURRICULUM D19R2 -- THE RE-GRADE SUCCESSOR. NO NEW COMPUTE.

D19R's phase 1 RAN CLEAN -- MESH, X2, S8, N2, S1, R1 all rc=0, chain_rc=0, the
selector wrote its step, 12.416 core-min against 13.6 predicted, every arm inside
its cap -- and its grader REFUSED, rc=2, emitting no verdict.  The arms are bought
and on disk.  THIS MODULE GRADES THOSE ARMS, WITH D19R's REGISTERED GATES, AS
REGISTERED, AND SPENDS ZERO SOLVER CORE-MINUTES.

`PREREGISTRATION.md` IN THIS DIRECTORY governs; nothing here may move a gate, a
threshold, a band, a cap or a label.

--------------------------------------------------------------------------
(I) WHY A SUCCESSOR AND NOT A REPAIR OF D19R's GRADER.
--------------------------------------------------------------------------
D19R has HAD FIRST COMPUTE, so its gates are closed and editing its frozen grader
is a `VERIFICATION_CHARTER.md` section 2d.1 question this family has refused FOUR
times.  A successor sidesteps 2d.1 entirely and is this family's established
pattern: SO-1cR, D19R itself, SO-3aR2, D4S-F3SR, A2-B2R.  **D19R's grader is NOT
EDITED BY THIS ITEM.**  It is IMPORTED, and its bytes are pinned below.

--------------------------------------------------------------------------
(II) THE DEFECT, D19R-GRADER-DEF-1 -- AND THERE ARE **TWO** BLOCKERS, NOT ONE.
--------------------------------------------------------------------------
Both were MEASURED on the frozen bytes, not read off a report.

**BLOCKER 1 -- THE CALL SITE IS IN THE WRONG PLACE, ON THE WRONG OBJECT.**
`d19r_grade.py:482` is the FIRST statement of `grade()`:

    prov = PROV.require_travelling_provenance({}, refuse=refuse)

`d19r_precondition.py:97-119` reads `out.get("verdict")` off that literal `{}`,
gets `None`, finds `None` not in `VOCAB`, and refuses -- BEFORE A SINGLE GATE IS
READ, thirty lines before composition.  As coded, D19R cannot emit a phase-1
verdict on ANY input.

**THE GUARD IS NOT THE DEFECT.**  Its own docstring says what it is for: *"Called
on the output object immediately before it is written ... Returns `out` unchanged
on success so it can wrap an emit expression directly."*  DRIVEN in `selftest()`
below: called correctly it **RETURNS THE OBJECT**, and it still REFUSES all three
ways of getting it wrong.  What the call site did was conflate TWO DIFFERENT
FUNCTIONS -- `read_upstream()`, which READS the provenance so it can be published
as gate `G19R-1i`, and `require_travelling_provenance(out)`, which ENFORCES that
the provenance travels attached to the verdict.  D19R called the ENFORCER where
the READER belonged, on an empty dict, at the top instead of the bottom.  That
`prov` is then published as `gates["G19R-1i"]` at `:508` is the tell: a gate
reading was expected there, and the enforcer never returns one.

**BLOCKER 2 -- AND IT IS NOT IN THE PUBLISHED DIAGNOSIS.  MOVING THE CALL WOULD
NOT HAVE BEEN ENOUGH.**  MEASURED on the frozen bytes: D19R's emit object
contains the key `"verdict_suffix"` ONCE and the keys `"provenance"` and
`"verdict_statement"` **ZERO TIMES**.  The guard requires BOTH of the latter --
it compares `out["provenance"]["md5"]`/`["path"]` against the upstream it reads,
and it requires `SUFFIX` to appear inside `out["verdict_statement"]`.  So a repair
that only relocated the call to wrap the emit would have refused a SECOND time, on
`provenance_not_carried`, and a third on `suffix_absent_from_verdict_statement`,
because the suffix is carried under a DIFFERENT KEY NAME.  This module fixes BOTH,
and `selftest()` drives the second one explicitly against D19R's own emit shape.

--------------------------------------------------------------------------
(III) HOW "NO GATE MOVED" IS PROVED RATHER THAN PROMISED.
--------------------------------------------------------------------------
**THIS MODULE CONTAINS NO GATE, NO THRESHOLD, NO BAND, NO CAP AND NO LABEL.**  It
re-implements nothing.  Every gate function -- `g_completion`, `g_planted`,
`g_reproduction`, `g_plateau`, `g_decomposition`, `g_disposition`, `g_toolchain`,
`g_caps` -- and every registered constant is reached through the imported frozen
module `F`, never copied.  A value that is not present cannot be moved.

Two driven checks stand behind that sentence, because an unenforced claim about
one's own source is worth nothing:
  * `pin_check()` refuses unless `d19r_grade.py` and `d19r_precondition.py` hash
    to the values frozen in `PREREGISTRATION.md` section 4.
  * `shadow_sweep()` parses THIS FILE's own AST and refuses if it assigns any name
    that is a registered constant of `F`.  `selftest()` drives it RED against a
    planted shadow, because a sweep that has never reported a finding is not
    known to be able to.

NO `assert` STATEMENT APPEARS IN THIS FILE: `python3 -O` strips them, so an assert
is not a guard (L-332).  `count_asserts()` proves it and is itself driven against
a planted assert.

Exit 2 on any refusal.  A refusal is NOT A RESULT, never a degraded verdict.
"""

import ast
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_D19R = os.path.normpath(os.path.join(_HERE, "..", "curriculum_D19R"))
if _D19R not in sys.path:
    sys.path.insert(0, _D19R)

# ---- THE FROZEN INSTRUMENTS, IMPORTED AND NEVER COPIED ----------------------
import d19r_grade as F            # noqa: E402  every gate and every constant
import d19r_precondition as PROV  # noqa: E402  the guard, unchanged

ITEM = "D19R2"
PREDECESSOR = "D19R"
# The run root is D19R's OWN.  This item creates no run root and stages nothing.
BASE = F.BASE

# ---- SECTION 4 PINS.  Existence is asserted BEFORE any md5 (DAFOAM section 18.3).
FROZEN_PINS = {
    "d19r_grade.py": "707ccb0c8ace88d7f171a2e7299fde13",
    "d19r_precondition.py": "c66fff1e4d07573d774523b5e39ad813",
}

# Registered constants of `F` that this module may never shadow.  Named
# explicitly, because a sweep over "everything uppercase" would silently stop
# covering a constant the day one is renamed.
REGISTERED_CONSTANT_NAMES = (
    "ARMS_REQUIRED", "ARM_KIND", "ARM_RANKS", "ARTEFACT", "TERMINAL", "CAPS",
    "PREDICTED_CORE_MIN", "ITEM_CEILING_CORE_MIN", "NON_GRADING_ARMS",
    "STEPS_SWEEP", "DECADE_STRIDE", "COMPONENTS", "FUNCTIONS", "REPRO_FD_PCT",
    "REPRO_ADJ_PCT", "PLATEAU_TOL_PCT", "DECOMP_TOL_PCT", "NEAR_ZERO_ABS",
    "CTRL_STEP", "PLANT_K", "PLANT_K_SHRUNK", "GRADER_PLANT_K",
    "IMG_DIGEST_PATCHED", "CPUSET_REGISTERED", "VOCAB", "RESULT_LABELS",
    "INPUT_SUBDIRS",
)


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def pin_check(refuse=None):
    """Existence FIRST and SEPARATELY, then md5.  Returns the readings."""
    refuse = refuse or F.refuse
    out = {}
    for name in sorted(FROZEN_PINS):
        p = os.path.join(_D19R, name)
        if not os.path.isfile(p):
            refuse("D19R2-PIN", {"frozen_dependency_absent_before_any_md5": p})
        out[name] = {"path": p, "frozen": FROZEN_PINS[name]}
    for name in sorted(FROZEN_PINS):
        got = md5_of(out[name]["path"])
        out[name]["got"] = got
        if got != FROZEN_PINS[name]:
            refuse("D19R2-PIN", {"frozen_dependency_md5_drifted": name,
                                 "got": got, "frozen": FROZEN_PINS[name]})
    return {"verdict": "PASS", "pins": out,
            "note": "D19R's grader and guard are IMPORTED, never edited by this item"}


def shadow_sweep(path=None, refuse=None):
    """Refuse if THIS file assigns any registered constant of `F`.

    The proof that no gate, threshold, band, cap or label moved: this module does
    not contain one to move."""
    refuse = refuse or F.refuse
    src = open(path or os.path.abspath(__file__), "r").read()
    assigned = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    assigned.add(t.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)
    clash = sorted(assigned & set(REGISTERED_CONSTANT_NAMES))
    if clash:
        refuse("D19R2-SHADOW", {"module_shadows_a_registered_constant": clash})
    return {"verdict": "PASS", "n_registered_checked": len(REGISTERED_CONSTANT_NAMES),
            "n_assigned_in_this_module": len(assigned), "shadowed": []}


def count_asserts(path=None):
    src = open(path or os.path.abspath(__file__), "r").read()
    return sum(1 for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Assert))


# ================= composition ==============================================
def compose(repro, comp, tool, plateau, decomp, caps, refuse=None):
    """D19R's registered composition, transcribed and DRIVEN BRANCH BY BRANCH.

    This is the ONE piece of logic this module carries, because `F.grade()` cannot
    be called -- its first statement refuses.  Every branch is driven in
    `selftest()`, in the registered order, so the transcription is checked rather
    than trusted.  A GATE FAIL is never softened."""
    refuse = refuse or F.refuse
    if repro["verdict"] != "PASS":
        verdict, why = "NOT A RESULT", "G19R-1a: not the same instrument D19 ran"
    elif comp["verdict"] != "PASS" or tool["verdict"] != "PASS":
        verdict, why = "NOT A RESULT", "G19R-1h/G19R-1f"
    elif plateau["verdict"] != "PASS":
        verdict, why = "GATE FAIL", "G19R-1b: no two-sided decade-bracketed plateau at s*"
    elif decomp["verdict"] != "PASS":
        verdict, why = "GATE FAIL", "G19R-1d: np=1 and np=2 disagree at s*"
    elif caps["verdict"] != "PASS":
        verdict, why = "GATE FAIL", "G19R-1g: cap exceeded"
    else:
        verdict, why = "PASS", "all phase-1 gates PASS"
    if verdict not in F.VOCAB:
        refuse("VOCAB", {"verdict": verdict})
    return verdict, why


def grade(root):
    pins = pin_check()
    shadow = shadow_sweep()

    # ---- THE READ HALF.  This is what gate G19R-1i publishes, and it is
    # ---- `read_upstream()` -- NOT the enforcer.  BLOCKER 1 repaired.
    prov = PROV.read_upstream(refuse=F.refuse)

    ledger = F.read_ledger(os.path.join(root, "ledger.txt"))
    comp = F.g_completion(root, ledger)

    S8 = F.read_json(os.path.join(root, "S8", "d19r_S.json"), "S8")
    X = F.read_json(os.path.join(root, "X2", "d19r_X.json"), "X2")
    S1 = F.read_json(os.path.join(root, "S1", "d19r_S1.json"), "S1")
    N2 = F.read_json(os.path.join(root, "N2", "d19r_N.json"), "N2")
    R1 = F.read_json(os.path.join(root, "R1", "d19r_R1.json"), "R1")
    sel = F.read_json(os.path.join(root, "d19r_selected_step.json"), "selector")

    if sel.get("selector_saw_adjoint") is not False:
        F.refuse("G19R-1b", {"selector_not_adjoint_blind": True})
    if N2.get("grades_nothing") is not True or R1.get("grades_nothing") is not True:
        F.refuse("G19R-1e", {"non_grading_arm_does_not_declare_itself": True})

    planted = F.g_planted(S8, os.path.join(root, "S8", "d19r_S.json"))
    repro = F.g_reproduction(S8, X)
    plateau = F.g_plateau(S8, sel)
    decomp = F.g_decomposition(S8, S1, sel)
    disp = F.g_disposition(S8, X, plateau)
    tool = F.g_toolchain(ledger, root)
    caps = F.g_caps(ledger)

    gates = {"G19R-1a": repro, "G19R-1b": plateau, "G19R-1c": planted,
             "G19R-1d": decomp, "G19R-1e": disp, "G19R-1f": tool,
             "G19R-1g": caps, "G19R-1h": comp, "G19R-1i": prov}

    verdict, why = compose(repro, comp, tool, plateau, decomp, caps)
    phase2 = (verdict == "PASS")

    out = {
        "item": ITEM, "regrades": PREDECESSOR, "phase": 1, "root": root,
        "rows": {"PATCHED": verdict},
        "row_note": "PHASE 1 IS PATCHED-ROW ONLY, registered before compute "
                    "(D19R PREREGISTRATION.md section 9): the plateau is a property of the "
                    "PRIMAL and the STEP, which both images share, so a SHIPPED sweep "
                    "would reproduce this one by construction.  A DAFoam verdict is "
                    "normally TWO ROWS and phase 2, if ever reached, is two.",
        "verdict": verdict, "verdict_reason": why,
        # ---- BLOCKER 2 REPAIRED.  D19R's emit carried NEITHER of these keys --
        # ---- it spelled the suffix as `verdict_suffix` and carried no
        # ---- provenance block at all -- so relocating the call alone would have
        # ---- refused twice more.
        "provenance": prov,
        "verdict_statement": "%s %s" % (verdict, PROV.SUFFIX),
        "verdict_suffix": PROV.SUFFIX,
        "result_label": plateau.get("result_label"),
        "result_label_note": "V-NOPLATEAU is a REGISTERED RESULT that travels BESIDE the "
                             "verdict.  GATE FAIL is the verdict; V-NOPLATEAU is what was "
                             "learned; neither softens the other.  It reads 'no plateau of "
                             "half-decade width or greater', never 'no plateau'.",
        "phase2_eligible": phase2,
        "phase2_note": "PHASE 2 IS NOT AUTHORISED BY THIS GRADER.  Eligibility is gated on "
                       "G19R-1b PASS and on nothing else; G19R-1e cannot launch it.",
        "gates": gates,
        "measurement_arms_grading_nothing": {
            "N2": {"purpose": "the PERTURBED-MESH noise floor",
                   "rows": N2.get("n_rows"), "eta_raw": N2.get("eta_raw")},
            "R1": {"purpose": "sensitivity-equalised step DIAGNOSTIC",
                   "kappa": R1.get("kappa"), "ladder": R1.get("r1_ladder"),
                   "verdict": "DIAGNOSTIC"}},
        "regrade_provenance": {
            "arms_graded": "D19R phase 1, UNCHANGED and NOT RE-RUN",
            "new_solver_core_min": 0.0,
            "why_a_successor": "D19R has had first compute, so its gates are closed and a "
                               "repair of its grader is a VERIFICATION_CHARTER section 2d.1 "
                               "question this family has refused four times.  D19R's grader "
                               "is IMPORTED here, not edited.",
            "defect": "D19R-GRADER-DEF-1, TWO blockers: (1) d19r_grade.py:482 calls the "
                      "provenance ENFORCER as the first statement of grade(), on a literal "
                      "{}, where the READER belonged; (2) D19R's emit object carries "
                      "NEITHER `provenance` NOR `verdict_statement`, so relocating the call "
                      "alone would still have refused twice.",
            "pins": pins, "shadow_sweep": shadow,
            "no_gate_moved": "this module re-implements no gate and defines no registered "
                             "constant; every threshold, band, cap and label is reached "
                             "through the imported frozen module and is proved unshadowed "
                             "by shadow_sweep()"},
    }
    # ---- THE ENFORCE HALF, WHERE THE GUARD WAS DESIGNED TO BE CALLED: wrapping
    # ---- the emit, on the real output object, so it cannot be forgotten.
    return PROV.require_travelling_provenance(out, refuse=F.refuse)


# ================= selftest =================================================
def selftest():
    ran = [0]
    bad = [0]

    def leg(name, cond, detail=""):
        ran[0] += 1
        if not cond:
            bad[0] += 1
        print("   %-58s %s %s" % (name, "OK" if cond else "**FAILED**", detail))

    print("D19R2 GRADER SELFTEST")

    print(" A. the frozen dependencies")
    p = pin_check()
    leg("A1 both frozen pins exist and agree", p["verdict"] == "PASS")
    leg("A2 pin_check REFUSES on a drifted md5", _refuses(
        lambda: pin_check(refuse=_raise)) if _swap_pin() else False)
    _restore_pin()

    print(" B. THE DEFECT THIS ITEM EXISTS TO FIX -- reproduced on the frozen bytes")
    leg("B1 D19R's call form REFUSES (blocker 1)",
        _refuses(lambda: PROV.require_travelling_provenance({}, refuse=_raise)))
    src19 = open(os.path.join(_D19R, "d19r_grade.py")).read()
    leg("B2 D19R's emit carries NO `provenance` key (blocker 2)",
        '"provenance":' not in src19)
    leg("B3 D19R's emit carries NO `verdict_statement` key (blocker 2)",
        '"verdict_statement":' not in src19)

    print(" C. THE GUARD IS SOUND -- IT RETURNS, and it still refuses every wrong way")
    up = PROV.read_upstream()
    good = {"verdict": "GATE FAIL", "provenance": up,
            "verdict_statement": "GATE FAIL " + PROV.SUFFIX}
    r = PROV.require_travelling_provenance(dict(good))
    leg("C1 RETURNS on a correct emit", isinstance(r, dict) and r["verdict"] == "GATE FAIL")
    leg("C2 refuses a verdict outside VOCAB", _refuses(
        lambda: PROV.require_travelling_provenance(dict(good, verdict="fine"), refuse=_raise)))
    leg("C3 refuses provenance not carried", _refuses(
        lambda: PROV.require_travelling_provenance(dict(good, provenance={}), refuse=_raise)))
    leg("C4 refuses the suffix stripped", _refuses(
        lambda: PROV.require_travelling_provenance(
            dict(good, verdict_statement="GATE FAIL"), refuse=_raise)))

    print(" D. NO GATE MOVED -- and the sweep is driven RED")
    s = shadow_sweep()
    leg("D1 this module shadows no registered constant", s["verdict"] == "PASS",
        "checked %d" % s["n_registered_checked"])
    planted = ("PLATEAU_TOL_PCT = 999.0\n" + open(os.path.abspath(__file__)).read())
    leg("D2 the sweep REFUSES on a PLANTED shadow", _refuses(
        lambda: _sweep_text(planted)))
    for n in REGISTERED_CONSTANT_NAMES:
        if not hasattr(F, n):
            leg("D3 registered constant %s is reachable on F" % n, False)
            break
    else:
        leg("D3 every registered constant is reachable on the frozen module", True,
            "%d names" % len(REGISTERED_CONSTANT_NAMES))

    print(" E. the composition, EVERY registered branch driven")
    P = {"verdict": "PASS"}
    Bd = {"verdict": "GATE FAIL"}
    NR = {"verdict": "NOT A RESULT"}
    cases = [("repro fail -> NOT A RESULT", (NR, P, P, P, P, P), "NOT A RESULT"),
             ("completion fail -> NOT A RESULT", (P, Bd, P, P, P, P), "NOT A RESULT"),
             ("toolchain fail -> NOT A RESULT", (P, P, Bd, P, P, P), "NOT A RESULT"),
             ("plateau fail -> GATE FAIL", (P, P, P, Bd, P, P), "GATE FAIL"),
             ("decomposition fail -> GATE FAIL", (P, P, P, P, Bd, P), "GATE FAIL"),
             ("caps fail -> GATE FAIL", (P, P, P, P, P, Bd), "GATE FAIL"),
             ("all PASS -> PASS", (P, P, P, P, P, P), "PASS")]
    for name, args, want in cases:
        got, _ = compose(*args)
        leg("E %s" % name, got == want, "got %s" % got)
    leg("E precedence: repro fail beats plateau fail",
        compose(NR, P, P, Bd, P, P)[0] == "NOT A RESULT")

    print(" F. L-332")
    leg("F1 no assert statement in this file", count_asserts() == 0)
    leg("F2 count_asserts sees a planted assert",
        _count_text("assert True\n") == 1)

    print("D19R2 SELFTEST: %d legs, %d failed" % (ran[0], bad[0]))
    return 0 if bad[0] == 0 else 1


class _Planted(Exception):
    pass


def _raise(where, detail):
    raise _Planted("%s %s" % (where, json.dumps(detail, sort_keys=True, default=str)))


def _refuses(fn):
    try:
        fn()
    except (_Planted, PROV.Refusal, F.Refusal):
        return True
    return False


def _sweep_text(text):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(text)
        p = fh.name
    try:
        return shadow_sweep(p, refuse=_raise)
    finally:
        os.unlink(p)


def _count_text(text):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(text)
        p = fh.name
    try:
        return count_asserts(p)
    finally:
        os.unlink(p)


_PIN_SAVED = {}


def _swap_pin():
    _PIN_SAVED.update(FROZEN_PINS)
    FROZEN_PINS["d19r_grade.py"] = "0" * 32
    return True


def _restore_pin():
    FROZEN_PINS.update(_PIN_SAVED)


def main():
    argv = sys.argv[1:]
    if "--selftest" in argv:
        return selftest()
    root, out = BASE, None
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
        if a == "--out" and i + 1 < len(argv):
            out = argv[i + 1]
    try:
        res = grade(root)
    except (F.Refusal, PROV.Refusal) as exc:
        sys.stderr.write("D19R2_GRADE REFUSED: %s\n" % exc)
        return 2
    txt = json.dumps(res, indent=1, sort_keys=True, default=str)
    if out:
        with open(out, "w") as fh:
            fh.write(txt)
            fh.flush()
            os.fsync(fh.fileno())
    print("D19R2_GRADE verdict=%s label=%s reason=%s"
          % (res["verdict"], res.get("result_label"), res["verdict_reason"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
