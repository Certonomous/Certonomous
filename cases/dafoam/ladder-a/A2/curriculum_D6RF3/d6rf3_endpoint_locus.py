#!/usr/bin/env python3
"""Curriculum D6RF -- THE ENDPOINT LOCUS INSTRUMENT for the MULTIPOINT producer.

DERIVED FROM `cases/dafoam/ladder-a/A2/curriculum_D4/d4_endpoint_locus.py`
(md5 `e63df1845771c3e67457443918f5b82e`).  ZERO BYTES of that file are edited;
this is a separate file in a separate item, and the delta is enumerated in
`PREREGISTRATION.md` section 7a.  The two controls, both tolerances, the refusal
discipline and the selftest shape are D4's and are not re-derived here.

WHY A NEW FILE AT ALL, MEASURED RATHER THAN ASSERTED.  D4's parser was pointed
at D6R's producer and it REFUSED:

    parse_registration: {"add_design_var_first_arg_not_a_literal_string": true}

`d6r_opt_runScript.py:217-218` registers the three per-point angle-of-attack
design variables inside a loop --

    for pt in POINTS:
        self.add_design_var("patchV_" + pt, lower=[U0, 0.0], upper=[U0, 10.0],
                            scaler=0.1)

-- so the design-variable NAME is built at run time from a module-level list.
D4's parser refuses a non-literal first argument, which is the correct behaviour
for D4's registration and the reason the D6 lineage has never had a locus
control at all.  THE ONE DELTA IS THE PARSER, and it is a WIDENING of exactly
one form: `<string literal> + <name bound by a for-loop over a module-level list
of strings>`.  Every other form still REFUSES, and the widening is DRIVEN
against mutants in `--selftest` rather than promised here.

THE DEFECT THIS FILE EXISTS TO CATCH, and it is live in the D6 lineage TODAY.
OpenMDAO's pyOptSparseDriver applies each design variable's `scaler` BEFORE
pyOptSparse sees the problem, so `OptView.hst` holds DRIVER-SCALED values and
the extractor's `getValues(..., scale=False)` argument is INERT.  MEASURED on
D4's own preserved artefacts:

    d4_endpoint_dvs_DRIVERSCALED.json : patchV[0] = 10.0    shape[0] = 3.1690
    d4_endpoint_dvs_PHYSICAL.json     : patchV[0] = 100.0   shape[0] = 0.3169

`d6r_extract_endpoint.py` carries the same inert flag and has NO physical
repair beside it, and `d6r_fd_endpoint.py:97` feeds its output straight into
`prob.set_val`, which is PHYSICAL.  `shape`'s registered scaler is 10.0 and its
registered bounds are [-1, 1], so an unrepaired `F_mp` sets the wing to ten
times its deformation -- which is D4's arm F, `rc=1` at 15 s,
`AnalysisError: Mesh quality error!`
(`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/ledger.txt`,
`ARM=F`, and the log's own traceback).

WHY THE CRASH WAS LUCK, restated because it is the whole reason for CONTROL P.
Had `shape`'s scaler been 1.0, every primal would have converged and the arm
would have produced a complete, well-formed, plausible FD table AT A DESIGN
POINT THAT IS NOT THE ONE REGISTERED.  A units error is invisible to every
count-, plant- and order-based control in this family.

NEITHER CONTROL GRADES ANYTHING.  Both are near-identities:

  CONTROL P -- THE PINNED WITNESS.  A design-variable component whose registered
  `lower` EQUALS its registered `upper` cannot be moved by any optimiser; its
  physical value is DEFINITIONAL.  This producer has THREE, one per point:
  `patchV_cl04[0]`, `patchV_cl05[0]`, `patchV_cl06[0]`, each pinned at `U0`.
  The control does NOT know that in advance -- it DISCOVERS them by scanning the
  registration and REFUSES IF IT FINDS NONE (L-302).

  CONTROL B -- BOUNDS CONTAINMENT.  IPOPT does not violate bound constraints, so
  a reconstructed component outside its registered bounds is a units or indexing
  error, not a design point.

THE SCALERS ARE READ FROM THE REGISTERING SOURCE, NEVER TYPED.  A constant
copied into this file could drift from the registration and would reintroduce
the defect somewhere new.

TOLERANCES are D4's, verbatim, and are representation tolerances, not bands:
TOL_PINNED_REL = 1.0e-12 (four orders of margin on one IEEE-754 divide, and four
orders tighter than the smallest error the control exists to catch, a factor of
ten); TOL_BOUNDS_ABS = 1.0e-9 against bounds of order 1-100.  Neither is a gate,
a threshold, a band or a label, and neither moves one.

REFUSES (exit 2) rather than degrading.

Self-test: `python3 d6rf_endpoint_locus.py --selftest` builds deliberate mutants
and requires each control and each parser clause to FIRE.  A control not shown
able to refuse is not evidence (CLAUDE.md rule 3's principle, applied to a guard
rather than a zero).
"""
import argparse
import ast
import json
import os
import sys

# --- representation tolerances (NOT gates, NOT bands -- see the docstring) ---
TOL_PINNED_REL = 1.0e-12
TOL_BOUNDS_ABS = 1.0e-9

DV_KEYS_MIN = 3          # the registration must carry at least this many DVs


class LocusRefusal(Exception):
    pass


def refuse(where, detail):
    raise LocusRefusal("%s: %s" % (where, json.dumps(detail, sort_keys=True,
                                                     default=str)[:1500]))


# --------------------------------------------------------------- the parser
def _const_scope(tree):
    """Module-level `NAME = <number>` and `NAME = [<str>, ...]` assignments.

    Numbers give `U0`; string lists give `POINTS`.  Both are READ, never typed.
    """
    nums = {}
    strlists = {}
    for node in tree.body:
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            continue
        name = node.targets[0].id
        val = node.value
        if isinstance(val, ast.Constant) and isinstance(val.value, (int, float)) \
                and not isinstance(val.value, bool):
            nums[name] = float(val.value)
        elif isinstance(val, (ast.List, ast.Tuple)) and val.elts and all(
                isinstance(e, ast.Constant) and isinstance(e.value, str)
                for e in val.elts):
            strlists[name] = [e.value for e in val.elts]
    return nums, strlists


def _loop_bindings(tree, strlists):
    """`for <name> in <module-level list of str>:` -> {name: [values]}.

    THE ONE WIDENING over D4's parser.  A loop variable bound TWICE to different
    lists is AMBIGUOUS and REFUSES; a loop over anything but a module-level list
    of strings contributes nothing, so a design-variable name built from it
    still refuses downstream.
    """
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        if not isinstance(node.target, ast.Name):
            continue
        if not isinstance(node.iter, ast.Name):
            continue
        vals = strlists.get(node.iter.id)
        if vals is None:
            continue
        prev = out.get(node.target.id)
        if prev is not None and prev != vals:
            refuse("loop_bindings",
                   {"loop_variable": node.target.id,
                    "bound_to_two_different_lists": [prev, vals],
                    "note": "an ambiguous loop variable cannot name a design "
                            "variable; this parser refuses rather than picking"})
        out[node.target.id] = vals
    return out


def _dv_names(first_arg, loopvars, where):
    """Resolve an `add_design_var` first argument to the list of names it makes.

    ACCEPTS exactly two forms and REFUSES every other one:
      * a literal string                       -> [that string]
      * `"<literal>" + <loop variable>`        -> [literal + v for v in values]
    """
    if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
        return [first_arg.value]
    if isinstance(first_arg, ast.BinOp) and isinstance(first_arg.op, ast.Add) \
            and isinstance(first_arg.left, ast.Constant) \
            and isinstance(first_arg.left.value, str) \
            and isinstance(first_arg.right, ast.Name):
        vals = loopvars.get(first_arg.right.id)
        if vals is None:
            refuse(where,
                   {"name_concatenation_operand_is_not_a_loop_variable_over_a_"
                    "module_level_string_list": first_arg.right.id,
                    "known_loop_variables": sorted(loopvars)})
        return [first_arg.left.value + v for v in vals]
    refuse(where, {"add_design_var_first_arg_unsupported_form":
                   type(first_arg).__name__,
                   "supported": ['"literal"',
                                 '"literal" + <for-loop var over a module list '
                                 'of strings>']})


def _eval_bound(node, scope, where):
    """A deliberately tiny evaluator: number, name-from-scope, -x, or a list."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            refuse(where, {"unsupported_constant": repr(node.value)})
        return float(node.value)
    if isinstance(node, ast.Name):
        if node.id not in scope:
            refuse(where, {"name_not_a_module_level_constant": node.id,
                           "known": sorted(scope)})
        return scope[node.id]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval_bound(node.operand, scope, where)
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval_bound(e, scope, where) for e in node.elts]
    refuse(where, {"unsupported_expression_node": type(node).__name__})


def parse_registration(runscript_path):
    """Return {'source', 'module_constants', 'point_lists', 'dvs'}.

    REFUSES if fewer than DV_KEYS_MIN design variables are registered, if any is
    missing lower/upper/scaler, if a name is built by an unsupported form, or if
    two `add_design_var` calls register the SAME name with different records.
    """
    with open(runscript_path) as fh:
        src = fh.read()
    tree = ast.parse(src, filename=runscript_path)
    scope, strlists = _const_scope(tree)
    loopvars = _loop_bindings(tree, strlists)

    dvs = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else None)
        if name != "add_design_var":
            continue
        if not node.args:
            refuse("parse_registration", {"add_design_var_has_no_arguments": True})
        names = _dv_names(node.args[0], loopvars, "parse_registration")
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        rec = {}
        for need in ("lower", "upper", "scaler"):
            if need not in kw:
                refuse("parse_registration",
                       {"design_variable": names, "missing_keyword": need,
                        "found_keywords": sorted(kw)})
            rec[need] = _eval_bound(kw[need], scope,
                                    "parse_registration/%s/%s" % (names, need))
        if not isinstance(rec["scaler"], float):
            refuse("parse_registration",
                   {"design_variable": names, "scaler_is_not_a_scalar": rec["scaler"]})
        if rec["scaler"] == 0.0:
            refuse("parse_registration", {"design_variable": names, "scaler_is_zero": True})
        for dv in names:
            if dv in dvs and dvs[dv] != rec:
                refuse("parse_registration",
                       {"design_variable_registered_twice_with_different_records": dv,
                        "first": dvs[dv], "second": rec})
            dvs[dv] = rec

    if len(dvs) < DV_KEYS_MIN:
        refuse("parse_registration",
               {"design_variables_found": sorted(dvs),
                "n_found": len(dvs), "n_required_min": DV_KEYS_MIN,
                "note": "a registration this parser cannot read in full is a "
                        "registration it must not silently half-apply"})
    return {"source": os.path.abspath(runscript_path),
            "module_constants": scope, "point_lists": strlists,
            "loop_bindings": loopvars, "dvs": dvs}


# ------------------------------------------------------ bounds as per-index
def _expand(bound, n, where, what):
    """A registered bound is either a scalar (applies to every index) or a list
    of exactly n entries.  Anything else REFUSES rather than being broadcast."""
    if isinstance(bound, list):
        if len(bound) != n:
            refuse(where, {"bound": what, "len_registered": len(bound),
                           "len_extracted": n})
        return [float(x) for x in bound]
    return [float(bound)] * n


# -------------------------------------------------------------- the descale
def descale(scaled, reg):
    """Divide every extracted family by ITS registered scaler."""
    dvs = reg["dvs"]
    out = {}
    used = {}
    for k, vals in scaled.items():
        if k not in dvs:
            refuse("descale", {"extracted_key_not_registered": k,
                               "registered": sorted(dvs)})
        s = dvs[k]["scaler"]
        out[k] = [float(v) / s for v in vals]
        used[k] = s
    missing = sorted(set(dvs) - set(scaled))
    if missing:
        refuse("descale", {"registered_but_not_extracted": missing,
                           "note": "the extractor returned fewer design "
                                   "variables than the producer registered"})
    return out, used


# ------------------------------------------------------- CONTROL P (pinned)
def control_pinned(physical, reg):
    """Every component with lower == upper is DEFINITIONAL.  Assert each.

    REFUSES if it finds NO pinned component -- a control with nothing to check
    is not a control (L-302).
    """
    dvs = reg["dvs"]
    found = []
    bad = []
    for k in sorted(physical):
        if k not in dvs:
            refuse("control_pinned", {"component_not_registered": k,
                                      "registered": sorted(dvs)})
        n = len(physical[k])
        lo = _expand(dvs[k]["lower"], n, "control_pinned/%s" % k, "lower")
        hi = _expand(dvs[k]["upper"], n, "control_pinned/%s" % k, "upper")
        for i in range(n):
            if lo[i] != hi[i]:
                continue
            want = lo[i]
            got = physical[k][i]
            denom = abs(want) if want != 0.0 else 1.0
            rel = abs(got - want) / denom
            rec = {"dv": k, "idx": i, "pinned_value": want,
                   "reconstructed": got, "rel_residual": rel}
            found.append(rec)
            if rel > TOL_PINNED_REL:
                bad.append(rec)
    result = {"control": "P_PINNED_WITNESS", "n_pinned_found": len(found),
              "tol_rel": TOL_PINNED_REL, "witnesses": found, "violations": bad}
    if not found:
        refuse("control_pinned",
               {"n_pinned_found": 0,
                "note": "no design-variable component has lower == upper, so "
                        "this control checked nothing; a control with nothing "
                        "to check is not a control (L-302)"})
    if bad:
        refuse("control_pinned", {"violations": bad, "tol_rel": TOL_PINNED_REL})
    result["verdict"] = "PASS"
    return result


# ------------------------------------------------------- CONTROL B (bounds)
def control_bounds(physical, reg):
    """A reconstructed component outside its registered bounds is a units or
    indexing error, not a design point."""
    dvs = reg["dvs"]
    viol = []
    n_checked = 0
    worst = None
    for k in sorted(physical):
        if k not in dvs:
            refuse("control_bounds", {"component_not_registered": k,
                                      "registered": sorted(dvs)})
        n = len(physical[k])
        lo = _expand(dvs[k]["lower"], n, "control_bounds/%s" % k, "lower")
        hi = _expand(dvs[k]["upper"], n, "control_bounds/%s" % k, "upper")
        for i in range(n):
            n_checked += 1
            v = physical[k][i]
            over = max(lo[i] - v, v - hi[i])
            if worst is None or over > worst[0]:
                worst = (over, {"dv": k, "idx": i, "value": v,
                                "lower": lo[i], "upper": hi[i], "excess": over})
            if over > TOL_BOUNDS_ABS:
                viol.append({"dv": k, "idx": i, "value": v,
                             "lower": lo[i], "upper": hi[i], "excess": over})
    if n_checked == 0:
        refuse("control_bounds",
               {"n_checked": 0,
                "note": "zero components checked; a loop that can iterate zero "
                        "times asserts its own trip count"})
    result = {"control": "B_BOUNDS_CONTAINMENT", "n_checked": n_checked,
              "tol_abs": TOL_BOUNDS_ABS, "n_violations": len(viol),
              "violations": viol[:20],
              "closest_to_a_bound": worst[1] if worst else None}
    if viol:
        refuse("control_bounds", {"n_violations": len(viol),
                                  "n_checked": n_checked, "first_20": viol[:20]})
    result["verdict"] = "PASS"
    return result


# ------------------------------------------------------------- the gate mode
def gate(physical_json, runscript):
    """G-DVL -- re-read the PUBLISHED physical artefact from disk and re-assert
    both controls at GRADING time.  Never trusts the producer's own say-so."""
    reg = parse_registration(runscript)
    if not os.path.isfile(physical_json):
        refuse("G-DVL", {"physical_artifact_absent": physical_json})
    with open(physical_json) as fh:
        doc = json.load(fh)
    if doc.get("_units") != "PHYSICAL":
        refuse("G-DVL", {"_units": doc.get("_units"), "required": "PHYSICAL"})
    phys = {k: [float(x) for x in doc[k]] for k in reg["dvs"] if k in doc}
    if len(phys) != len(reg["dvs"]):
        refuse("G-DVL", {"design_variables_in_artifact": sorted(phys),
                         "registered": sorted(reg["dvs"])})
    p = control_pinned(phys, reg)
    b = control_bounds(phys, reg)
    return {"gate": "G-DVL_ENDPOINT_LOCUS", "verdict": "PASS",
            "artifact": os.path.abspath(physical_json),
            "registration_source": reg["source"],
            "scalers_registered": {k: reg["dvs"][k]["scaler"] for k in reg["dvs"]},
            "control_P": p, "control_B": b}


# ------------------------------------------------------------- the self-test
_MUT_SRC = '''
POINTS = ["cl04", "cl05", "cl06"]


class T:
    def f(self):
        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        for pt in POINTS:
            self.add_design_var("patchV_" + pt, lower=[U0, 0.0],
                                upper=[U0, 10.0], scaler=0.1)
'''


def _mut_file(tmp, name, body):
    p = os.path.join(tmp, name)
    with open(p, "w") as fh:
        fh.write(body)
    return p


def selftest():
    import tempfile
    ok, fail = [], []

    def check(label, fn, want_refusal):
        try:
            fn()
            got, detail = "no-refusal", ""
        except LocusRefusal as e:
            got, detail = "REFUSED", str(e)[:150]
        except Exception as e:                                  # noqa: BLE001
            got, detail = "EXCEPTION:%s" % type(e).__name__, str(e)[:150]
        want = "REFUSED" if want_refusal else "no-refusal"
        print("  %-58s want=%-11s got=%-11s %s" % (
            label, want, got, "PASS" if got == want else "FAIL")
            + (("   <%s>" % detail) if detail and got == want else ""))
        (ok if got == want else fail).append(label)

    tmp = tempfile.mkdtemp(prefix="d6rf_locus_st_")
    hdr = "U0 = 100.0\n"

    # ---------------- the CLEAN control: everything must pass ----------------
    clean = _mut_file(tmp, "clean.py", hdr + _MUT_SRC)
    reg = parse_registration(clean)
    print("SELFTEST clean: design variables parsed = %s" % json.dumps(sorted(reg["dvs"])))
    scaled = {"twist": [-0.28020223162835683],
              "shape": [6.024591873823496, -6.024591873823496],
              "patchV_cl04": [10.0, 0.1195966323219245],
              "patchV_cl05": [10.0, 0.15],
              "patchV_cl06": [10.0, 0.19]}
    phys, used = descale(scaled, reg)
    print("SELFTEST clean: scalers read from source = %s" % json.dumps(used, sort_keys=True))
    check("clean/control_P (3 pinned witnesses expected)",
          lambda: control_pinned(phys, reg), False)
    check("clean/control_B", lambda: control_bounds(phys, reg), False)
    cp = control_pinned(phys, reg)
    n_pin_ok = cp["n_pinned_found"] == 3
    print("  PLANT: exactly 3 pinned witnesses discovered (one per point)     %s"
          % ("PASS" if n_pin_ok else "FAIL  n=%d" % cp["n_pinned_found"]))
    (ok if n_pin_ok else fail).append("plant/three-pinned-witnesses")

    # ------ THE ACTUAL DEFECT VECTOR: both controls MUST fire on it ---------
    check("driver-scaled vector (the live defect)/control_P",
          lambda: control_pinned({k: list(v) for k, v in scaled.items()}, reg), True)
    check("driver-scaled vector (the live defect)/control_B",
          lambda: control_bounds({k: list(v) for k, v in scaled.items()}, reg), True)

    # ---------------- CONTROL P mutants ----------------
    m = {k: list(v) for k, v in phys.items()}
    m["patchV_cl05"][0] = 100.0 * (1.0 + 1.0e-9)
    check("mutant/one pinned witness off by 1e-9 relative",
          lambda: control_pinned(m, reg), True)
    m2 = {k: list(v) for k, v in phys.items()}
    m2["patchV_cl06"][0] = 10.0
    check("mutant/one pinned witness left driver-scaled (10.0)",
          lambda: control_pinned(m2, reg), True)
    m3 = {k: list(v) for k, v in phys.items()}
    m3["patchV_cl04"][0] = 100.0 * (1.0 + 1.0e-13)
    check("mutant/pinned off by 1e-13 (inside tol, must NOT fire)",
          lambda: control_pinned(m3, reg), False)
    nopin = _mut_file(tmp, "nopin.py", hdr + _MUT_SRC.replace(
        'lower=[U0, 0.0],', 'lower=[0.0, 0.0],'))
    regnp = parse_registration(nopin)
    check("registration with zero pinned components/control_P",
          lambda: control_pinned(phys, regnp), True)

    # ---------------- CONTROL B mutants ----------------
    b1 = {k: list(v) for k, v in phys.items()}
    b1["shape"][0] = 1.0 + 1.0e-6
    check("mutant/shape just above upper bound", lambda: control_bounds(b1, reg), True)
    b2 = {k: list(v) for k, v in phys.items()}
    b2["twist"][0] = -10.5
    check("mutant/twist below lower bound", lambda: control_bounds(b2, reg), True)
    b3 = {k: list(v) for k, v in phys.items()}
    b3["shape"][0] = 1.0 + 1.0e-12
    check("mutant/shape above bound by 1e-12 (inside tol, must NOT fire)",
          lambda: control_bounds(b3, reg), False)
    check("empty component set/control_B", lambda: control_bounds({}, reg), True)

    # ---------------- PARSER mutants: the WIDENING is bounded ---------------
    check("parser/scaler keyword removed",
          lambda: parse_registration(_mut_file(tmp, "noscaler.py", hdr + _MUT_SRC.replace(
              ' scaler=0.1)', ')'))), True)
    check("parser/lower keyword removed",
          lambda: parse_registration(_mut_file(tmp, "nolower.py", hdr + _MUT_SRC.replace(
              'lower=-1.0, ', ''))), True)
    check("parser/only two design variables registered",
          lambda: parse_registration(_mut_file(tmp, "twodv.py", hdr + _MUT_SRC.replace(
              '        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)\n', '')
              .replace('        for pt in POINTS:\n'
                       '            self.add_design_var("patchV_" + pt, lower=[U0, 0.0],\n'
                       '                                upper=[U0, 10.0], scaler=0.1)\n', ''))), True)
    check("parser/U0 not a module-level constant",
          lambda: parse_registration(_mut_file(tmp, "nou0.py", _MUT_SRC)), True)
    check("parser/scaler is zero",
          lambda: parse_registration(_mut_file(tmp, "zeroscaler.py", hdr + _MUT_SRC.replace(
              'scaler=10.0', 'scaler=0.0'))), True)
    check("parser/POINTS is not a module-level list (name unresolvable)",
          lambda: parse_registration(_mut_file(tmp, "nopoints.py", hdr + _MUT_SRC.replace(
              'POINTS = ["cl04", "cl05", "cl06"]', 'POINTS = _elsewhere()'))), True)
    check("parser/loop over a non-list name",
          lambda: parse_registration(_mut_file(tmp, "loopcall.py", hdr + _MUT_SRC.replace(
              'for pt in POINTS:', 'for pt in range(3):'))), True)
    check("parser/name built by an f-string (unsupported form)",
          lambda: parse_registration(_mut_file(tmp, "fstr.py", hdr + _MUT_SRC.replace(
              '"patchV_" + pt', 'f"patchV_{pt}"'))), True)
    check("parser/name built from a variable alone (unsupported form)",
          lambda: parse_registration(_mut_file(tmp, "bare.py", hdr + _MUT_SRC.replace(
              '"patchV_" + pt', 'pt'))), True)
    check("parser/same loop variable bound to two different lists",
          lambda: parse_registration(_mut_file(tmp, "ambig.py",
              hdr + 'OTHER = ["a", "b"]\n' + _MUT_SRC
              + '\n        for pt in OTHER:\n            pass\n')), True)

    # ---------------- DESCALE mutants ----------------
    check("descale/extracted key the registration does not know",
          lambda: descale(dict(scaled, alpha=[1.0]), reg), True)
    check("descale/extractor returned fewer DVs than registered",
          lambda: descale({"twist": [-0.28]}, reg), True)
    check("descale/bound list length != extracted length",
          lambda: control_bounds({"twist": [0.0], "shape": [0.0],
                                  "patchV_cl04": [100.0, 1.0, 2.0],
                                  "patchV_cl05": [100.0, 1.0],
                                  "patchV_cl06": [100.0, 1.0]}, reg), True)

    # -------- THE PARSER IS READING THE REAL PRODUCER, not a fixture --------
    real = os.environ.get(
        "D6RF_RUNSCRIPT",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                     "curriculum_D6R", "d6r_opt_runScript.py"))
    real = os.path.abspath(real)
    if os.path.isfile(real):
        rr = parse_registration(real)
        sc = {k: rr["dvs"][k]["scaler"] for k in sorted(rr["dvs"])}
        print("SELFTEST real d6r_opt_runScript.py scalers = %s" % json.dumps(sc, sort_keys=True))
        print("SELFTEST real d6r_opt_runScript.py U0      = %r"
              % rr["module_constants"].get("U0"))
        print("SELFTEST real d6r_opt_runScript.py POINTS  = %r"
              % rr["point_lists"].get("POINTS"))
        expect = {"patchV_cl04": 0.1, "patchV_cl05": 0.1, "patchV_cl06": 0.1,
                  "shape": 10.0, "twist": 0.1}
        # PLANTS (L-325): values known to exist, confirming the parser can
        # express the names it is asked about on the REAL producer.
        print("  PLANT: the five registered names and their scalers          %s"
              % ("PASS" if sc == expect else "FAIL  got=%s" % json.dumps(sc, sort_keys=True)))
        (ok if sc == expect else fail).append("plant/real-runscript-scalers")
        u0ok = rr["module_constants"].get("U0") == 100.0
        print("  PLANT: U0 read from the source, not typed here              %s"
              % ("PASS" if u0ok else "FAIL"))
        (ok if u0ok else fail).append("plant/real-U0")
        ptok = rr["point_lists"].get("POINTS") == ["cl04", "cl05", "cl06"]
        print("  PLANT: POINTS read from the source, not typed here          %s"
              % ("PASS" if ptok else "FAIL"))
        (ok if ptok else fail).append("plant/real-POINTS")
        # and the real producer's three pinned witnesses must be DISCOVERED
        rphys = {"twist": [0.0], "shape": [0.0],
                 "patchV_cl04": [100.0, 1.0], "patchV_cl05": [100.0, 1.0],
                 "patchV_cl06": [100.0, 1.0]}
        rp = control_pinned(rphys, rr)
        pinok = rp["n_pinned_found"] == 3
        print("  PLANT: 3 pinned witnesses discovered on the REAL producer    %s"
              % ("PASS" if pinok else "FAIL  n=%d" % rp["n_pinned_found"]))
        (ok if pinok else fail).append("plant/real-pinned-witnesses")
    else:
        print("  FAIL: the real producer %s is not readable; the real-source "
              "plants did NOT run" % real)
        fail.append("plant/real-producer-absent")

    print("\nD6RF_LOCUS_SELFTEST %d/%d PASS" % (len(ok), len(ok) + len(fail)))
    if fail:
        print("FAILED: %s" % ", ".join(fail))
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gate", metavar="PHYSICAL_JSON")
    ap.add_argument("--runscript", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.gate or not a.runscript:
        sys.stderr.write("usage: d6rf_endpoint_locus.py --selftest | "
                         "--gate <physical.json> --runscript <producer.py> "
                         "[--out F]\n")
        return 64
    try:
        res = gate(a.gate, a.runscript)
    except LocusRefusal as e:
        sys.stderr.write("D6RF_LOCUS REFUSE %s\n" % e)
        return 2
    txt = json.dumps(res, indent=1, sort_keys=True)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(txt)
            fh.flush()
            os.fsync(fh.fileno())
    print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
