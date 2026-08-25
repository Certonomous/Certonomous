#!/usr/bin/env python3
"""Consumer-derived completeness guards for cfd launchers and graders.

WHY THIS FILE EXISTS — the one sentence that bounds it
------------------------------------------------------
**A HASH CAN ONLY EVER ANSWER "IS THIS THE SAME AS BEFORE". IT CAN NEVER ANSWER
"IS THIS ENOUGH".**

dafoam's D12 arrest: a launcher staged a field directory, hashed whatever was
there, and re-asserted that manifest faithfully before all 23 stages — passing
every time. The directory held FOUR fields; the solve needed ELEVEN. Every
stage died on ``cannot find file 0/nut``. Internally perfect, externally false.
A comparator-side md5 of the same directory would not have caught it either:
both readers agree on the same four files. That is L-321's shape — fixture and
checker sharing an assumption — applied to a manifest.

The repair, and the rule every function here obeys:

    **DERIVE THE REQUIRED SET FROM THE CONSUMER, NEVER FROM THE PRODUCER.**

The consumer of a staged ``0/`` is the solver, and what the solver will demand
is written in the case's OWN dictionaries — ``controlDict`` names the
application, ``fvSolution`` names the matrices it will assemble, ``fvSchemes``
names what is transported, ``turbulenceProperties`` names the closure, and
``thermophysicalProperties`` says whether the energy equation is solved at all.
Not one of those is a list of what happens to be in ``0/``.

NO ``assert`` ANYWHERE IN THIS FILE CARRIES A REFUSAL
-----------------------------------------------------
Binding cfd ruling of 2026-08-25: no ``assert`` in a cfd instrument may carry a
refusal, a guard, a control or a gate. ``python3 -O`` strips ``assert``, and
that was measured turning a guard into a no-op that then proceeded to act on
the shared tree. **Every refusal here is ``raise Refusal``**, and
``--selftest`` re-executes itself under ``-O`` to prove every refusal still
fires when assertions are stripped.

REFUSE RATHER THAN DEGRADE
--------------------------
An application or a turbulence model this file has no consumer map for is a
REFUSAL, never a pass. A guard that silently skips what it does not recognise
is the D12 defect one level up: it would answer "nothing missing" about a case
it never read.

STATUS: UNFIRED INSTRUMENT. This file grades nothing and is pinned by no
pre-registration. It is a library plus a selftest. Wiring it into a launcher
that has ALREADY FIRED is forbidden — standing rule 2 closes the grading path
at the pre-registration commit, and standing rule 6 forbids editing a frozen
file. See ``docs/standards/`` and the cfd exposure record for which cfd
instruments carry the D12 defect classes and may not be repaired in place.

Usage as a library:

    from staging_completeness import (
        require_staged_complete, resolve_field, require_write_compression,
        require_pinned_callgraph, last_value_by_quantity, Refusal)

Usage as a check:

    python3 scripts/staging_completeness.py --selftest
    python3 scripts/staging_completeness.py --case <case_dir>
    python3 scripts/staging_completeness.py --callgraph <launcher.py>
"""
from __future__ import annotations

import argparse
import ast
import gzip
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# REFUSAL — never an assert, never a warning, never a degraded pass.
# ---------------------------------------------------------------------------


class Refusal(Exception):
    """A guard refused. Raised, not asserted, so ``-O`` cannot strip it."""


def refuse(msg: str) -> None:
    raise Refusal(msg)


# ---------------------------------------------------------------------------
# CONSUMER MAPS.  Each entry answers "what will this consumer DEMAND", and is
# keyed on something the case itself declares.  An unmapped key is a refusal.
# ---------------------------------------------------------------------------

# Fields the solver DERIVES at run time and never reads from `0/`.  Every name
# here has to be justified, because a wrong entry in this set is exactly the
# false negative D12 suffered.
DERIVED_NEVER_STAGED = {
    "e", "h",        # energy: supplied through T by the thermo package
    "K", "Ekp",      # kinetic-energy terms, formed from U
    "phi", "phid",   # fluxes, formed from U (and rho)
    "rho",           # formed by the thermo package from (p, T)
    "nuEff", "muEff", "alphaEff", "thermo:mu", "thermo:alpha",
}

# application -> fields the solver demands in `0/` REGARDLESS of turbulence.
# `None` marks an application that stages nothing (a mesh/utility step).
APPLICATION_FIELDS = {
    "simpleFoam":              {"U", "p"},
    "pimpleFoam":              {"U", "p"},
    "icoFoam":                 {"U", "p"},
    "potentialFoam":           {"U", "p"},
    "rhoSimpleFoam":           {"U", "p", "T"},
    "rhoPimpleFoam":           {"U", "p", "T"},
    "rhoCentralFoam":          {"U", "p", "T"},
    "rhoCentralFoamBounded":   {"U", "p", "T"},
    "rhoCentralFoamBoundedDiag":     {"U", "p", "T"},
    "rhoCentralFoamInletUpwindDiag": {"U", "p", "T"},
    "sonicFoam":               {"U", "p", "T"},
    "interFoam":               {"U", "p_rgh", "alpha.water"},
    "interPhaseChangeFoam":    {"U", "p_rgh", "alpha.water"},
    "buoyantSimpleFoam":       {"U", "p", "p_rgh", "T"},
    "buoyantPimpleFoam":       {"U", "p", "p_rgh", "T"},
    "laplacianFoam":           {"T"},
    "scalarTransportFoam":     {"T"},
    "blockMesh":               None,
    "checkMesh":               None,
    "decomposePar":            None,
}

# Applications that solve a compressible energy equation.  With turbulence ON
# these additionally demand `alphat` — the turbulent thermal diffusivity — and
# that requirement appears in NO scheme and NO solver block, which is precisely
# why it cannot be derived from `fvSchemes`/`fvSolution` alone.
COMPRESSIBLE_APPLICATIONS = {
    "rhoSimpleFoam", "rhoPimpleFoam", "rhoCentralFoam",
    "rhoCentralFoamBounded", "rhoCentralFoamBoundedDiag",
    "rhoCentralFoamInletUpwindDiag", "sonicFoam",
    "buoyantSimpleFoam", "buoyantPimpleFoam",
}

# RASModel / LESModel -> the closure fields it demands in `0/`.
TURBULENCE_FIELDS = {
    "kOmegaSST":            {"k", "omega", "nut"},
    "kOmegaSSTQCR":         {"k", "omega", "nut"},
    "kOmegaSSTSparta":      {"k", "omega", "nut"},
    "kOmegaSSTCorrected":   {"k", "omega", "nut"},
    "kOmegaSSTFrozen":      {"k", "omega", "nut"},
    "AugmentedkOmegaSST":   {"k", "omega", "nut"},
    "kOmega":               {"k", "omega", "nut"},
    "kEpsilon":             {"k", "epsilon", "nut"},
    "RNGkEpsilon":          {"k", "epsilon", "nut"},
    "realizableKE":         {"k", "epsilon", "nut"},
    "SpalartAllmaras":      {"nuTilda", "nut"},
    "SSG":                  {"R", "epsilon", "nut"},
    "LRR":                  {"R", "epsilon", "nut"},
    "EBRSM":                {"R", "epsilon", "nut"},
    "kEqn":                 {"k", "nut"},
    "Smagorinsky":          {"nut"},
    "WALE":                 {"nut"},
}

# Every field ANY closure owns.  A turbulence field named in `fvSolution` but
# NOT owned by the closure this case declares is NOT required — see the
# INTERSECT in `required_fields`.
TURBULENCE_OWNED = set().union(*TURBULENCE_FIELDS.values())


# ---------------------------------------------------------------------------
# Dictionary reading.  Deliberately small and deliberately strict.
# ---------------------------------------------------------------------------


def strip_foam_comments(text: str) -> str:
    """Remove `/* */` and `//` comments.  A commented-out RASModel keyword must
    not be read as the model — this file met four of those in cfd's tree."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def read_dict(case_dir: str, *parts: str) -> str | None:
    p = os.path.join(case_dir, *parts)
    if not os.path.isfile(p):
        return None
    with open(p, "r", errors="replace") as fh:
        return strip_foam_comments(fh.read())


def expand_key(key: str) -> set:
    """`"(U|k|omega|e)"` -> {U, k, omega, e}; `p` -> {p}.

    OpenFOAM keys are regular expressions when quoted.  A reader that took the
    literal string would silently require a field named `(U|k|omega|e)` and
    find it missing, or — worse, and this is the direction that matters — would
    fail to require U, k and omega at all.
    """
    key = key.strip().strip('"')
    if not key:
        return set()
    if re.fullmatch(r"\(?[A-Za-z0-9_.:|]+\)?", key) and "|" in key:
        return {k for k in key.strip("()").split("|") if k}
    if re.search(r"[\[\]*+?^$]", key):
        # A genuine regex we cannot enumerate.  Refusing is the honest answer:
        # we cannot state the required set, so we must not claim completeness.
        refuse(f"fvSolution key {key!r} is a regex this reader cannot "
               f"enumerate; the required set cannot be derived and "
               f"completeness must not be claimed")
    return {key}


def solver_block_fields(fv_solution: str) -> set:
    """Every field that gets a matrix — read from the `solvers` block."""
    m = re.search(r"\bsolvers\b\s*\{", fv_solution)
    if not m:
        return set()
    i = m.end()
    depth, start = 1, i
    while i < len(fv_solution) and depth:
        if fv_solution[i] == "{":
            depth += 1
        elif fv_solution[i] == "}":
            depth -= 1
        i += 1
    block = fv_solution[start:i - 1]
    out = set()
    # Keys are the tokens that immediately precede a `{` at this level.
    for km in re.finditer(r'(^|\n)\s*("?[A-Za-z0-9_.:|()]+"?)\s*(\n\s*)?\{', block):
        out |= expand_key(km.group(2))
    return out


def transported_fields(fv_schemes: str) -> set:
    """Every field under a `div(phi,X)` / `div(phid,X)` scheme."""
    out = set()
    for m in re.finditer(r"div\(\s*phi[a-zA-Z]*\s*,\s*([A-Za-z0-9_.]+)\s*\)", fv_schemes):
        out.add(m.group(1))
    return out


def turbulence_model(turb_props: str | None) -> tuple[str, str]:
    """(simulationType, model).  An unmapped model is refused by the caller."""
    if turb_props is None:
        return ("laminar", "laminar")
    sm = re.search(r"\bsimulationType\s+([A-Za-z]+)\s*;", turb_props)
    sim = sm.group(1) if sm else "laminar"
    if sim.lower() == "laminar":
        return (sim, "laminar")
    mm = re.search(r"\b(?:RASModel|LESModel|model)\s+([A-Za-z0-9_]+)\s*;", turb_props)
    if not mm:
        refuse(f"turbulenceProperties declares simulationType {sim} but names "
               f"no RASModel/LESModel; the closure field set cannot be derived")
    on = re.search(r"\bturbulence\s+(on|off|true|false)\s*;", turb_props)
    if on and on.group(1) in ("off", "false"):
        return (sim, "laminar")
    return (sim, mm.group(1))


def application_of(control_dict: str | None) -> str:
    if control_dict is None:
        refuse("no system/controlDict — the consumer cannot be identified, so "
               "the required field set cannot be derived")
    m = re.search(r"\bapplication\s+([A-Za-z0-9_]+)\s*;", control_dict)
    if not m:
        refuse("system/controlDict names no `application`; the consumer cannot "
               "be identified")
    return m.group(1)


# ---------------------------------------------------------------------------
# THE COMPLETENESS ASSERTION.  Consumer-derived, refusing, never an assert.
# ---------------------------------------------------------------------------


def required_fields(case_dir: str) -> tuple[set, dict]:
    """The field set THE SOLVER WILL DEMAND, derived from the case's own
    dictionaries.  Returns (required, provenance) where provenance names which
    dictionary contributed each field, so a refusal can be argued with rather
    than merely believed.
    """
    control = read_dict(case_dir, "system", "controlDict")
    app = application_of(control)
    if app not in APPLICATION_FIELDS:
        refuse(f"application {app!r} has no consumer map in "
               f"staging_completeness.APPLICATION_FIELDS; this guard REFUSES "
               f"rather than report a case it cannot read as complete")
    base = APPLICATION_FIELDS[app]
    prov: dict = {}
    if base is None:
        return set(), {"application": app, "note": "utility; stages no fields"}

    req = set(base)
    for f in base:
        prov[f] = f"controlDict application {app}"

    # WHAT THE CLOSURE OWNS is decided by turbulenceProperties and by nothing
    # else.  Read FIRST, so the intersect below can use it.
    turb = read_dict(case_dir, "constant", "turbulenceProperties")
    sim, model = turbulence_model(turb)
    if model != "laminar" and model not in TURBULENCE_FIELDS:
        refuse(f"turbulence model {model!r} has no consumer map in "
               f"staging_completeness.TURBULENCE_FIELDS; this guard REFUSES "
               f"rather than claim completeness for a closure it cannot "
               f"enumerate")
    closure = set(TURBULENCE_FIELDS[model]) if model != "laminar" else set()

    # fvSolution / fvSchemes, INTERSECTED WITH THE CLOSURE on turbulence fields.
    # An OpenFOAM solver regex is written for BREADTH and routinely names more
    # than the case runs: `"(U|k|epsilon|omega|e)"` in a kOmegaSST case names
    # `epsilon`, which that case neither solves nor stores.  Taking the regex
    # literally DEMANDS `epsilon` AND FALSELY REFUSES A CORRECT CASE.
    #
    # THE MAP FROM SOLVER KEYS TO FILES IN `0/` IS NOT THE IDENTITY, IN EITHER
    # DIRECTION: `e` is solved but not stored; `alphat` and `nut` are stored but
    # never named as solver keys.  A check must be shown not to refuse a correct
    # run as well as shown to refuse an incomplete one — both directions, or it
    # is not a check.
    dict_derived = set()
    fv_sol = read_dict(case_dir, "system", "fvSolution")
    if fv_sol:
        for f in solver_block_fields(fv_sol):
            dict_derived.add(f)
            prov.setdefault(f, "fvSolution solvers block")
    fv_sch = read_dict(case_dir, "system", "fvSchemes")
    if fv_sch:
        for f in transported_fields(fv_sch):
            dict_derived.add(f)
            prov.setdefault(f, "fvSchemes divSchemes")
    dict_derived -= DERIVED_NEVER_STAGED
    dict_derived -= (TURBULENCE_OWNED - closure)     # <- the INTERSECT
    req |= dict_derived

    for f in closure:
        req.add(f)
        prov.setdefault(f, f"turbulenceProperties {sim}/{model}")
    if closure and app in COMPRESSIBLE_APPLICATIONS:
        # alphat is demanded by the COMPRESSIBLE wall functions and appears in
        # no scheme and no solver block.  This is the UNION limb: a field
        # required as an initial condition but never named as a solver key.
        req.add("alphat")
        prov.setdefault("alphat", f"compressible {app} + turbulence {model}")

    req -= DERIVED_NEVER_STAGED
    return req, prov


def resolve_field(dirpath: str, name: str) -> str | None:
    """Resolve a field by THE NAME THE CASE ACTUALLY WRITES.

    ``writeCompression on`` makes fields ``U.gz``; an age guard keyed on the
    bare name then never finds its datum and reports a missing field where a
    perfectly good one sits beside it.  Returns the resolved path, or None if
    NEITHER form exists.  The caller refuses on None — an unreadable datum is
    never a pass.
    """
    for cand in (name, name + ".gz"):
        p = os.path.join(dirpath, cand)
        if os.path.isfile(p):
            return p
    return None


def require_staged_complete(case_dir: str, stage_dir: str = "0") -> dict:
    """REFUSE unless every field the consumer demands is present in `stage_dir`.

    This is the D12 assertion.  It does not ask whether the staged tree matches
    a manifest; it asks whether the staged tree is ENOUGH.
    """
    req, prov = required_fields(case_dir)
    stage = os.path.join(case_dir, stage_dir)
    if not req:
        return {"application_stages_nothing": True, "provenance": prov}
    if not os.path.isdir(stage):
        refuse(f"{case_dir}: no {stage_dir}/ directory, but the consumer "
               f"demands {len(req)} fields: {sorted(req)}")
    missing, resolved = [], {}
    for f in sorted(req):
        p = resolve_field(stage, f)
        if p is None:
            missing.append(f"{f}  (required by {prov.get(f, 'consumer')})")
        else:
            resolved[f] = os.path.basename(p)
    if missing:
        refuse(f"{case_dir}: STAGED TREE IS NOT ENOUGH — the consumer demands "
               f"{len(req)} fields and {len(missing)} are ABSENT from "
               f"{stage_dir}/:\n  " + "\n  ".join(missing) +
               f"\npresent: {sorted(os.listdir(stage))}")
    return {"required": sorted(req), "resolved": resolved, "provenance": prov}


def require_write_compression(case_dir: str, expected: str = "off") -> dict:
    """REFUSE unless controlDict REGISTERS `writeCompression`.

    A registered setting and an inherited default are DIFFERENT SAFETY
    POSITIONS and this lab's records must not blur them.  A case that omits the
    keyword is relying on an OpenFOAM version default that nothing in the
    repository asserts; that reliance is legal only when stated, so this guard
    refuses silence and makes the reliance explicit at the call site.
    """
    control = read_dict(case_dir, "system", "controlDict")
    if control is None:
        refuse(f"{case_dir}: no system/controlDict")
    m = re.search(r"\bwriteCompression\s+(\w+)\s*;", control)
    if not m:
        refuse(f"{case_dir}: controlDict REGISTERS NO writeCompression. Its "
               f"field naming is inherited from a version-dependent OpenFOAM "
               f"default that nothing here asserts. Register it explicitly "
               f"(`writeCompression {expected};`) or resolve every field "
               f"through resolve_field(), which accepts both `f` and `f.gz`.")
    got = m.group(1)
    if got != expected:
        refuse(f"{case_dir}: controlDict registers writeCompression {got}, "
               f"expected {expected}")
    return {"writeCompression": got, "registered": True}


# ---------------------------------------------------------------------------
# CALL-GRAPH COMPLETENESS.  The F12 defect: iterating the PINNED set instead of
# the CALLED set.  A 27th function added to the grading path is simply not in
# the dict and is never checked.
# ---------------------------------------------------------------------------


def module_calls(py_path: str, alias_map: dict) -> set:
    """Every `ALIAS.name(...)` call the file makes, as `module.name`.

    Walks the AST rather than grepping, because a grep for the pinned names
    finds exactly the names already pinned — the same circularity one level up.
    """
    with open(py_path, "r", errors="replace") as fh:
        tree = ast.parse(fh.read())
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and isinstance(n.func.value, ast.Name):
            base = n.func.value.id
            if base in alias_map:
                out.add(f"{alias_map[base]}.{n.func.attr}")
    return out


def require_pinned_callgraph(py_path: str, pinned: set, alias_map: dict,
                             allow: set | None = None) -> dict:
    """REFUSE if the file CALLS anything into a pinned module that is not pinned.

    Iterates the CALLED set, not the pinned set.  This is the direction that
    answers "is this enough".  ``allow`` is for calls deliberately excluded,
    and every entry in it is a claim someone has to defend in review.
    """
    called = module_calls(py_path, alias_map)
    allow = allow or set()
    unpinned = sorted(called - set(pinned) - allow)
    if unpinned:
        refuse(f"{py_path}: THE PIN SET IS NOT ENOUGH — this file CALLS "
               f"{len(unpinned)} function(s) into pinned modules that the pin "
               f"dict does not cover, so their bytes are never checked:\n  " +
               "\n  ".join(unpinned) +
               "\nA hash over the pinned set cannot see these: it answers "
               "'is this the same', not 'is this enough'.")
    return {"called": sorted(called), "pinned_covering": True,
            "allowed": sorted(allow)}


def require_no_assert_nodes(py_path: str) -> dict:
    """ARM (c): REFUSE if the file contains ANY `assert` statement.

    The cheapest of the three arms and the only one that CATCHES A REVERT
    WITHOUT RUNNING ANYTHING. Driving a suite under `-O` proves the refusals
    that EXIST still fire; it cannot see an `assert` reintroduced on a path the
    suite does not drive. This can.

    Note the failure mode it defends against, which is why "the selftest passes
    under -O" is the weak test: had a guard's behavioural coverage itself been
    asserts, the property would evaporate silently under `-O` AND EVERY
    MUTATION TEST WOULD STILL PASS — because selftests run under plain
    `python3`. The battery and the hole live under different flags.
    """
    with open(py_path, "r", errors="replace") as fh:
        tree = ast.parse(fh.read(), filename=py_path)
    hits = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assert)]
    if hits:
        refuse(f"{py_path}: {len(hits)} `assert` statement(s) at line(s) "
               f"{hits} — `python3 -O` STRIPS THESE ENTIRELY. No assert in a "
               f"cfd instrument may carry a refusal, a guard, a control or a "
               f"gate. Use `raise` or `sys.exit`.")
    return {"assert_nodes": 0, "path": py_path}


# ---------------------------------------------------------------------------
# SHARED-TOKEN READING.  D12's third finding: the frozen reader took "the LAST
# `average:` value" where the solver prints `average:` on TWO lines, so it read
# CL instead of CD — 93.9 % off against a 1e-12 tolerance.
# ---------------------------------------------------------------------------


def last_value_by_quantity(text: str, quantity: str, token: str = "average:",
                           number: str = r"[-+0-9.eE]+") -> float:
    """The last value of `token` ANCHORED ON `quantity`, refusing if the token
    is shared.

    Anchor on the quantity name; never on a token two quantities share.  If
    `token` appears on lines that do not carry `quantity`, this refuses rather
    than return the one that happened to be last — that ordering is an accident
    of the writer, not a property of the quantity.
    """
    tok = re.escape(token)
    bearing = [ln for ln in text.splitlines() if re.search(tok, ln)]
    if not bearing:
        refuse(f"token {token!r} appears nowhere; the reader cannot be shown "
               f"able to see a value, so its answer is not evidence")
    named = [ln for ln in bearing if quantity in ln]
    if not named:
        refuse(f"token {token!r} appears on {len(bearing)} line(s), NONE of "
               f"which names {quantity!r}; a positional read would return "
               f"another quantity's value")
    if len(bearing) > len(named):
        others = [ln.strip()[:70] for ln in bearing if quantity not in ln]
        refuse(f"token {token!r} IS SHARED — it appears on {len(bearing)} "
               f"lines, only {len(named)} of which name {quantity!r}. A "
               f"'last match' read here returns whichever quantity the writer "
               f"printed last. Other bearers:\n  " + "\n  ".join(others[:5]))
    m = re.search(tok + r"\s*(" + number + r")", named[-1])
    if not m:
        refuse(f"line naming {quantity!r} carries {token!r} but no parseable "
               f"number: {named[-1].strip()[:80]!r}")
    return float(m.group(1))


# ---------------------------------------------------------------------------
# SELFTEST.  Every guard is shown REFUSING on a planted defect, and the whole
# suite is re-run under `-O` to prove no refusal was carried by an assert.
# ---------------------------------------------------------------------------


def _write(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def _build_case(root: str) -> str:
    """A minimal rhoSimpleFoam/kOmegaSST case, dictionaries copied in shape from
    verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79."""
    case = os.path.join(root, "case")
    _write(os.path.join(case, "system", "controlDict"),
           "application     rhoSimpleFoam;\nendTime 6000;\n"
           "writeFormat     ascii;\nwriteCompression off;\n")
    _write(os.path.join(case, "system", "fvSolution"),
           'solvers\n{\n    p\n    {\n        solver GAMG;\n    }\n'
           '    "(U|k|omega|e)"\n    {\n        solver PBiCGStab;\n    }\n}\n')
    _write(os.path.join(case, "system", "fvSchemes"),
           "divSchemes\n{\n    default none;\n    div(phi,U) bounded Gauss linearUpwind limited;\n"
           "    div(phi,e) $energy;\n    div(phi,K) $energy;\n    div(phi,Ekp) $energy;\n"
           "    div(phi,k) $turbulence;\n    div(phi,omega) $turbulence;\n"
           "    div(phid,p) Gauss upwind;\n}\n")
    _write(os.path.join(case, "constant", "turbulenceProperties"),
           "simulationType          RAS;\n\nRAS\n{\n    RASModel            kOmegaSST;\n"
           "    turbulence          on;\n}\n")
    _write(os.path.join(case, "constant", "thermophysicalProperties"),
           "thermoType\n{\n    type            hePsiThermo;\n}\n")
    for f in ("T", "U", "alphat", "k", "nut", "omega", "p"):
        _write(os.path.join(case, "0", f), f"// {f}\n")
    return case


def _fires(fn, *a, **kw) -> str:
    """Run `fn`; return the refusal message.  A guard that does NOT refuse here
    is itself the defect, and this raises rather than prints."""
    try:
        fn(*a, **kw)
    except Refusal as e:
        return str(e)
    raise SystemExit(
        f"SELFTEST FAILED: {getattr(fn, '__name__', fn)} DID NOT REFUSE on a "
        f"planted defect. A completeness check never seen to refuse is the "
        f"same defect one level up.")


def selftest() -> int:
    opt = "STRIPPED (-O)" if not __debug__ else "live (no -O)"
    print(f"staging_completeness --selftest   [assertions: {opt}]", flush=True)
    root = tempfile.mkdtemp(prefix="stagecomp_")
    try:
        case = _build_case(root)

        # --- C1: the derivation reproduces a REAL staged set exactly --------
        req, prov = required_fields(case)
        want = {"T", "U", "alphat", "k", "nut", "omega", "p"}
        if req != want:
            raise SystemExit(f"C1 FAILED: derived {sorted(req)} != {sorted(want)}")
        info = require_staged_complete(case)
        print(f"  C1 consumer-derived required set = {sorted(req)}")
        print(f"     matches the real F12 attempt-2 0/ exactly; PASSES when complete")

        # --- C1b: THE OTHER DIRECTION — a check must be shown NOT to refuse
        # a correct run.  Regex breadth: a kOmegaSST case whose fvSolution key
        # also names `epsilon`.  Taking the regex literally would demand a
        # field this case neither solves nor stores.
        wide = os.path.join(root, "wide")
        shutil.copytree(case, wide)
        _write(os.path.join(wide, "system", "fvSolution"),
               'solvers\n{\n    p\n    {\n solver GAMG;\n }\n'
               '    "(U|k|epsilon|omega|e)"\n    {\n solver PBiCGStab;\n }\n}\n')
        wreq, _ = required_fields(wide)
        if "epsilon" in wreq:
            raise SystemExit("C1b FAILED: regex breadth demanded `epsilon` of a "
                             "kOmegaSST case — this FALSELY REFUSES a correct run")
        require_staged_complete(wide)
        print("  C1b regex breadth `(U|k|epsilon|omega|e)` on kOmegaSST -> "
              "epsilon NOT demanded; correct case still PASSES")

        # --- C2: PLANTED CONTROL — remove one required field, must REFUSE ---
        os.remove(os.path.join(case, "0", "nut"))
        msg = _fires(require_staged_complete, case)
        if "nut" not in msg:
            raise SystemExit("C2 FAILED: refusal does not name the absent field")
        print(f"  C2 planted control: 0/nut removed -> REFUSED, names nut")
        _write(os.path.join(case, "0", "nut"), "// nut\n")

        # --- C2b: the D12 shape itself — a four-field tree for an 11-field solve
        thin = os.path.join(root, "thin")
        shutil.copytree(case, thin)
        for f in ("alphat", "k", "nut", "omega"):
            os.remove(os.path.join(thin, "0", f))
        msg = _fires(require_staged_complete, thin)
        print(f"  C2b D12 shape: 3-field 0/ for a 7-field consumer -> REFUSED")

        # --- C3: .gz resolution, and refusal when NEITHER form exists -------
        gzcase = os.path.join(root, "gzcase")
        shutil.copytree(case, gzcase)
        with open(os.path.join(gzcase, "0", "U"), "rb") as fi, \
                gzip.open(os.path.join(gzcase, "0", "U.gz"), "wb") as fo:
            shutil.copyfileobj(fi, fo)
        os.remove(os.path.join(gzcase, "0", "U"))
        if resolve_field(os.path.join(gzcase, "0"), "U") is None:
            raise SystemExit("C3 FAILED: resolve_field cannot see U.gz")
        require_staged_complete(gzcase)
        print("  C3 writeCompression limb: 0/U.gz resolved, case still complete")
        os.remove(os.path.join(gzcase, "0", "U.gz"))
        msg = _fires(require_staged_complete, gzcase)
        print("  C3b neither U nor U.gz -> REFUSED (unreadable is never a pass)")

        # --- C4: registered vs INHERITED writeCompression --------------------
        require_write_compression(case, "off")
        nodecl = os.path.join(root, "nodecl")
        shutil.copytree(case, nodecl)
        _write(os.path.join(nodecl, "system", "controlDict"),
               "application     rhoSimpleFoam;\nendTime 6000;\nwriteFormat ascii;\n")
        msg = _fires(require_write_compression, nodecl)
        if "REGISTERS NO writeCompression" not in msg:
            raise SystemExit("C4 FAILED: wrong refusal text")
        print("  C4 registered `off` accepted; ABSENT keyword -> REFUSED "
              "(inherited default is not a guarantee)")

        # --- C5: unmapped consumer REFUSES rather than degrades --------------
        unk = os.path.join(root, "unk")
        shutil.copytree(case, unk)
        _write(os.path.join(unk, "system", "controlDict"),
               "application     someNewFoam;\nwriteCompression off;\n")
        _fires(required_fields, unk)
        unkt = os.path.join(root, "unkt")
        shutil.copytree(case, unkt)
        _write(os.path.join(unkt, "constant", "turbulenceProperties"),
               "simulationType RAS;\nRAS\n{\n    RASModel myModel;\n    turbulence on;\n}\n")
        _fires(required_fields, unkt)
        print("  C5 unmapped application and unmapped RASModel -> both REFUSED")

        # --- C6: CALL-GRAPH completeness, with a planted 27th function -------
        lp = os.path.join(root, "launcher.py")
        _write(lp, "import x\ndef go():\n    W.build_case()\n    T.final_coefficient()\n")
        pinned = {"rae2822_case9.build_case", "tmr_verification.final_coefficient"}
        aliases = {"W": "rae2822_case9", "T": "tmr_verification"}
        require_pinned_callgraph(lp, pinned, aliases)
        _write(lp, "import x\ndef go():\n    W.build_case()\n    T.final_coefficient()\n"
                   "    T._foam(['rhoSimpleFoam'])\n")
        msg = _fires(require_pinned_callgraph, lp, pinned, aliases)
        if "tmr_verification._foam" not in msg:
            raise SystemExit("C6 FAILED: refusal does not name the unpinned call")
        print("  C6 planted 27th function on the call graph -> REFUSED, names it")

        # --- C6b: the live F12 launcher, read as a FINDING (never edited) ----
        f12 = pathlib.Path("/home/ubuntu/Certonomous/verification/runs/F12_runs/"
                           "mesh_ladder_attempt2_2026-08-25/launch_f12_rung.py")
        if f12.is_file():
            tree = ast.parse(f12.read_text(errors="replace"))
            pin = set()
            for n in ast.walk(tree):
                if isinstance(n, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "GRADING_FN_SHA256"
                        for t in n.targets):
                    pin = {k.value for k in n.value.keys}
            called = module_calls(str(f12), {"W": "rae2822_case9",
                                             "T": "tmr_verification",
                                             "HE": "head_engineer"})
            gap = sorted(called - pin)
            print(f"  C6b live F12 launcher: {len(pin)} pinned, {len(called)} "
                  f"called, UNPINNED-BUT-CALLED = {gap}")

        # --- C7: shared-token reading ---------------------------------------
        good = "Cd       average: 1.23e-02\n"
        if abs(last_value_by_quantity(good, "Cd") - 1.23e-02) > 1e-15:
            raise SystemExit("C7 FAILED: correct read did not return the value")
        shared = "Cd       average: 1.23e-02\nCl       average: 3.40e-01\n"
        msg = _fires(last_value_by_quantity, shared, "Cd")
        if "IS SHARED" not in msg:
            raise SystemExit("C7 FAILED: shared token not diagnosed")
        print("  C7 `average:` on two quantities -> REFUSED as SHARED "
              "(a last-match read would have returned Cl)")

        # --- C8: ARM (c) — zero Assert nodes, checked on THIS FILE ---------
        require_no_assert_nodes(os.path.abspath(__file__))
        planted = os.path.join(root, "planted.py")
        _write(planted, "def guard(x):\n    assert x > 0, 'refusal'\n    return x\n")
        msg = _fires(require_no_assert_nodes, planted)
        if "STRIPS THESE ENTIRELY" not in msg:
            raise SystemExit("C8 FAILED: wrong refusal text")
        print("  C8 arm (c): this file carries ZERO assert nodes; a planted "
              "`assert` guard -> REFUSED without running it")

        print(f"ALL CONTROLS FIRED  [assertions: {opt}]", flush=True)
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--no-recurse", action="store_true",
                    help="internal: suppress the -O re-execution")
    ap.add_argument("--case", help="check one case directory for completeness")
    ap.add_argument("--callgraph", help="report a launcher's unpinned calls")
    a = ap.parse_args()

    if a.case:
        info = require_staged_complete(a.case)
        print(f"{a.case}: COMPLETE against its own consumer")
        print(f"  required: {info.get('required')}")
        return 0

    if a.callgraph:
        called = module_calls(a.callgraph, {"W": "rae2822_case9",
                                            "T": "tmr_verification",
                                            "HE": "head_engineer"})
        print("\n".join(sorted(called)))
        return 0

    if a.selftest:
        rc = selftest()
        if rc == 0 and not a.no_recurse and __debug__:
            # THE -O CONTROL.  Every refusal above must still fire when
            # assertions are stripped.  If any guard had been written as an
            # `assert`, this pass is where it would vanish.
            print("\nRe-running the whole suite under `python3 -O` "
                  "(assertions stripped) ...")
            p = subprocess.run([sys.executable, "-O", os.path.abspath(__file__),
                                "--selftest", "--no-recurse"])
            if p.returncode != 0:
                print("REFUSAL VANISHED UNDER -O — a guard was carried by an "
                      "assert. This is the defect the cfd ruling forbids.")
                return 1
            print("-O pass: every refusal still fired.")
        return rc

    ap.print_help()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Refusal as e:
        sys.stderr.write("REFUSED: " + str(e) + "\n")
        raise SystemExit(2)
