#!/usr/bin/env python3
"""Curriculum D4 -- THE ENDPOINT LOCUS INSTRUMENT.  D4-DEF-4's answer.

WHAT THIS FILE IS FOR, in one sentence.  D4's registered gate set checks THAT n
components were measured and never checks WHERE they were measured; this file
supplies the two controls that establish WHERE, and it is the only thing in the
D4 instrument set that can say "the FD table is at the wrong design point".

THE DEFECT (D4-DEF-4, evidence in D4_DEF4_DEF5_ENDPOINT_SCALING.md, ruling in
SUPERVISOR_D4DEF4_REPAIR_RULING.md).  OpenMDAO's pyOptSparseDriver applies each
design variable's `scaler` BEFORE pyOptSparse sees the problem.  pyOptSparse's
own scale factor is therefore 1.0, its `scale` flag is a no-op, `OptView.hst`
holds DRIVER-SCALED values, and the frozen extractor's `getValues(..., scale=
False)` argument is INERT.  `d7_fd_endpoint.py` then applies those values as
PHYSICAL through `prob.set_val`.  `shape`'s registered scaler is 10.0, so arm F
set the wing to ten times its optimised deformation and destroyed the mesh.

WHY THE CRASH WAS LUCK.  Had `shape`'s scaler been 1.0, every primal would have
converged and arm F would have produced a complete, well-formed, plausible FD
table AT A DESIGN POINT THAT IS NOT THE OPTIMUM.  Five components requested,
five returned, in the registered order; every count refusal passing; G6's plant
seen; G6b's blind reader refused; all four G7 mutations raising their named
refusals.  THE FULLY ARMED INSTRUMENT SET WOULD HAVE CERTIFIED IT.  A units
error is invisible to every count-, plant- and order-based control in this
family.

THE TWO CONTROLS THIS FILE ADDS, and why each is unforgeable.

  CONTROL P -- THE PINNED WITNESS.  A design variable component whose registered
  `lower` EQUALS its registered `upper` cannot be moved by any optimiser: its
  physical value is DEFINITIONAL.  D4 has exactly one, `patchV[0]`, pinned at
  `U0`.  The control does NOT know that in advance -- it DISCOVERS every pinned
  component by scanning the registration, and REFUSES IF IT FINDS NONE, because
  a control with nothing to check is not a control (L-302).

  CONTROL B -- BOUNDS CONTAINMENT.  IPOPT does not violate bound constraints.
  A reconstructed component outside its registered bounds is therefore a units
  or indexing error, NOT an optimum.  62 of 96 `shape` components sat outside
  [-1, 1] in the arm-F extraction.

NEITHER CONTROL GRADES ANYTHING.  Both are near-identities and guards in the
sense of VERIFICATION_CHARTER.md 2d.1 condition (2): they have no direction to
be selected toward, because they do not know which direction a verdict wants.
That is why the repair they establish is admissible at all.

THE SCALERS ARE READ FROM THE REGISTERING SOURCE, NEVER TYPED.  `parse_
registration()` parses `d7_opt_runScript.py` with `ast` and takes `lower`,
`upper` and `scaler` from its `add_design_var` calls and `U0` from its own
module-level assignment.  A constant copied into this file could drift from the
registration and would reintroduce D4-DEF-4 somewhere new.  The parser REFUSES
when it cannot find all three keywords for every registered design variable.

TOLERANCES, and why they are representation tolerances and not bands.
  TOL_PINNED_REL = 1.0e-12.  IEEE-754 double carries ~2.2e-16 relative; one
  divide adds at most one ulp.  1.0e-12 is four orders of margin on the
  arithmetic and four orders TIGHTER than the smallest error this control
  exists to catch (a scaler of 0.1 misapplied is a factor of ten).  It cannot
  be tuned to admit a defect because no defect lives in that gap.
  TOL_BOUNDS_ABS = 1.0e-9, same reasoning against bounds of order 1-100.
Neither is a gate, a threshold, a band or a label, and neither moves one.

REFUSES (exit 2) rather than degrading, exactly as this family's comparators do.

Self-test: `python3 d7fr_endpoint_locus.py --selftest` builds deliberate mutants
and requires each control to FIRE.  A control not shown able to refuse is not
evidence (CLAUDE.md rule 3's principle, applied to a guard rather than a zero).
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
    """Module-level NAME = <number> assignments, so `U0` is READ, not typed."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, (int, float)) \
                and not isinstance(node.value.value, bool):
            out[node.targets[0].id] = float(node.value.value)
    return out


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
    """Return {'U0_scope': {...}, 'dvs': {name: {lower, upper, scaler}}}.

    REFUSES if fewer than DV_KEYS_MIN design variables are registered, or if any
    registered design variable is missing lower, upper or scaler.
    """
    with open(runscript_path) as fh:
        src = fh.read()
    tree = ast.parse(src, filename=runscript_path)
    scope = _const_scope(tree)

    dvs = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = fn.attr if isinstance(fn, ast.Attribute) else (
            fn.id if isinstance(fn, ast.Name) else None)
        if name != "add_design_var":
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant) \
                or not isinstance(node.args[0].value, str):
            refuse("parse_registration",
                   {"add_design_var_first_arg_not_a_literal_string": True})
        dv = node.args[0].value
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        rec = {}
        for need in ("lower", "upper", "scaler"):
            if need not in kw:
                refuse("parse_registration",
                       {"design_variable": dv, "missing_keyword": need,
                        "found_keywords": sorted(kw)})
            rec[need] = _eval_bound(kw[need], scope,
                                    "parse_registration/%s/%s" % (dv, need))
        if not isinstance(rec["scaler"], float):
            refuse("parse_registration",
                   {"design_variable": dv, "scaler_is_not_a_scalar": rec["scaler"]})
        if rec["scaler"] == 0.0:
            refuse("parse_registration", {"design_variable": dv, "scaler_is_zero": True})
        dvs[dv] = rec

    if len(dvs) < DV_KEYS_MIN:
        refuse("parse_registration",
               {"design_variables_found": sorted(dvs),
                "n_found": len(dvs), "n_required_min": DV_KEYS_MIN,
                "note": "a registration this parser cannot read in full is a "
                        "registration it must not silently half-apply"})
    return {"source": os.path.abspath(runscript_path),
            "module_constants": scope, "dvs": dvs}


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
    """Divide every extracted family by ITS registered scaler.

    REFUSES on any extracted design-variable key with no registered scaler --
    a key the registration does not know about cannot be corrected, and
    correcting it with someone else's factor is the defect wearing a new hat.
    """
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
              "tol_rel": TOL_PINNED_REL, "witnesses": found,
              "violations": bad}
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
    """IPOPT does not violate bound constraints, so a reconstructed component
    outside its registered bounds is a units or indexing error, not an optimum.
    """
    dvs = reg["dvs"]
    viol = []
    n_checked = 0
    worst = None
    for k in sorted(physical):
        n = len(physical[k])
        lo = _expand(dvs[k]["lower"], n, "control_bounds/%s" % k, "lower")
        hi = _expand(dvs[k]["upper"], n, "control_bounds/%s" % k, "upper")
        for i in range(n):
            n_checked += 1
            v = physical[k][i]
            over = max(lo[i] - v, v - hi[i])
            if worst is None or over > worst[0]:
                worst = (over, {"dv": k, "idx": i, "value": v,
                                "lower": lo[i], "upper": hi[i],
                                "excess": over})
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
                                  "n_checked": n_checked,
                                  "first_20": viol[:20]})
    result["verdict"] = "PASS"
    return result


# ------------------------------------------------------------- the gate mode
def gate(workdir, runscript, physical_json="d7_endpoint_dvs_PHYSICAL.json"):
    """H3 -- re-read the PUBLISHED physical artifact from disk and re-assert
    both controls at grading time.  Never trusts the producer's own say-so."""
    reg = parse_registration(runscript)
    path = os.path.join(workdir, physical_json)
    if not os.path.isfile(path):
        refuse("H3", {"physical_artifact_absent": path})
    with open(path) as fh:
        doc = json.load(fh)
    if doc.get("_units") != "PHYSICAL":
        refuse("H3", {"_units": doc.get("_units"), "required": "PHYSICAL"})
    phys = {k: [float(x) for x in doc[k]] for k in reg["dvs"] if k in doc}
    if len(phys) != len(reg["dvs"]):
        refuse("H3", {"design_variables_in_artifact": sorted(phys),
                       "registered": sorted(reg["dvs"])})
    p = control_pinned(phys, reg)
    b = control_bounds(phys, reg)
    return {"gate": "H3_ENDPOINT_LOCUS", "verdict": "PASS",
            "artifact": os.path.abspath(path),
            "registration_source": reg["source"],
            "scalers_registered": {k: reg["dvs"][k]["scaler"] for k in reg["dvs"]},
            "control_P": p, "control_B": b}


# ------------------------------------------------------------- the self-test
_MUT_SRC = '''
class T:
    def f(self):
        self.add_design_var("twist", lower=-10.0, upper=10.0, scaler=0.1)
        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)
        self.add_design_var("patchV", lower=[U0, 0.0], upper=[U0, 10.0], scaler=0.1)
'''


def _mut_file(tmp, name, body):
    p = os.path.join(tmp, name)
    with open(p, "w") as fh:
        fh.write(body)
    return p


def selftest():
    import tempfile
    ok = []
    fail = []

    def check(label, fn, want_refusal):
        try:
            fn()
            got = "no-refusal"
        except LocusRefusal as e:
            got = "REFUSED"
            detail = str(e)[:160]
        except Exception as e:                                  # noqa: BLE001
            got = "EXCEPTION:%s" % type(e).__name__
            detail = str(e)[:160]
        else:
            detail = ""
        want = "REFUSED" if want_refusal else "no-refusal"
        line = "  %-52s want=%-11s got=%-11s %s" % (label, want, got,
                                                    "PASS" if got == want else "FAIL")
        print(line + (("   <%s>" % detail) if detail and got == want else ""))
        (ok if got == want else fail).append(label)

    tmp = tempfile.mkdtemp(prefix="d7fr_locus_st_")
    hdr = "U0 = 291.6\n"

    # ---------------- the CLEAN control: everything must pass ----------------
    clean = _mut_file(tmp, "clean.py", hdr + _MUT_SRC)
    reg = parse_registration(clean)
    scaled = {"twist": [-0.28020223162835683],
              "shape": [6.024591873823496, -6.024591873823496],
              "patchV": [29.16, 0.30600000000000005]}
    phys, used = descale(scaled, reg)
    print("SELFTEST clean: scalers read from source = %s" % json.dumps(used, sort_keys=True))
    print("SELFTEST clean: physical = %s" % json.dumps(phys, sort_keys=True))
    check("clean/control_P", lambda: control_pinned(phys, reg), False)
    check("clean/control_B", lambda: control_bounds(phys, reg), False)

    # ------- THE ACTUAL D4-DEF-4 VECTOR: both controls MUST fire on it -------
    check("D4-DEF-4 raw driver-scaled vector/control_P",
          lambda: control_pinned({k: list(v) for k, v in scaled.items()}, reg), True)
    check("D4-DEF-4 raw driver-scaled vector/control_B",
          lambda: control_bounds({k: list(v) for k, v in scaled.items()}, reg), True)

    # ---------------- CONTROL P mutants ----------------
    m = {k: list(v) for k, v in phys.items()}
    m["patchV"][0] = 291.6 * (1.0 + 1.0e-9)
    check("mutant/pinned off by 1e-9 relative", lambda: control_pinned(m, reg), True)
    m2 = {k: list(v) for k, v in phys.items()}
    m2["patchV"][0] = 29.16
    check("mutant/pinned left driver-scaled (29.16 == THE MEASURED D7 WITNESS)", lambda: control_pinned(m2, reg), True)
    m3 = {k: list(v) for k, v in phys.items()}
    m3["patchV"][0] = 291.6 * (1.0 + 1.0e-13)
    check("mutant/pinned off by 1e-13 (inside tol, must NOT fire)",
          lambda: control_pinned(m3, reg), False)

    # a registration with NO pinned component: the control must refuse itself
    nopin = _mut_file(tmp, "nopin.py", hdr + _MUT_SRC.replace(
        'lower=[U0, 0.0], upper=[U0, 10.0]', 'lower=[0.0, 0.0], upper=[400.0, 10.0]'))
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
    check("empty component set/control_B",
          lambda: control_bounds({}, reg), True)

    # ---------------- PARSER mutants ----------------
    check("parser/scaler keyword removed",
          lambda: parse_registration(_mut_file(tmp, "noscaler.py", hdr + _MUT_SRC.replace(
              ', scaler=10.0', ''))), True)
    check("parser/lower keyword removed",
          lambda: parse_registration(_mut_file(tmp, "nolower.py", hdr + _MUT_SRC.replace(
              'lower=-1.0, ', ''))), True)
    check("parser/only two design variables registered",
          lambda: parse_registration(_mut_file(tmp, "twodv.py", hdr + _MUT_SRC.replace(
              '        self.add_design_var("shape", lower=-1.0, upper=1.0, scaler=10.0)\n', ''))), True)
    check("parser/U0 not a module-level constant",
          lambda: parse_registration(_mut_file(tmp, "nou0.py", _MUT_SRC)), True)
    check("parser/scaler is zero",
          lambda: parse_registration(_mut_file(tmp, "zeroscaler.py", hdr + _MUT_SRC.replace(
              'scaler=10.0', 'scaler=0.0'))), True)

    # ---------------- DESCALE mutants ----------------
    check("descale/extracted key the registration does not know",
          lambda: descale(dict(scaled, alpha=[1.0]), reg), True)
    check("descale/extractor returned fewer DVs than registered",
          lambda: descale({"twist": [-0.28]}, reg), True)
    check("descale/bound list length != extracted length",
          lambda: control_bounds({"twist": [0.0], "shape": [0.0],
                                  "patchV": [291.6, 1.0, 2.0]}, reg), True)

    # ---------- THE PARSER IS READING THE REAL FILE, not a fixture ----------
    here = os.path.dirname(os.path.abspath(__file__))
    # THE FROZEN RUNSCRIPT IS NOT DUPLICATED INTO THIS ITEM.  Two copies of a
    # frozen file are two chances for it to drift, so the plant reads the ONE
    # committed copy: beside this file when the launcher has staged it, else
    # `../curriculum_D7/d7_opt_runScript.py` at its committed path.
    real = None
    for cand in (os.path.join(here, "d7_opt_runScript.py"),
                 os.path.join(here, os.pardir, "curriculum_D7",
                              "d7_opt_runScript.py")):
        if os.path.isfile(cand):
            real = os.path.abspath(cand)
            break
    if real:
        rr = parse_registration(real)
        sc = {k: rr["dvs"][k]["scaler"] for k in sorted(rr["dvs"])}
        print("SELFTEST real %s" % real)
        print("SELFTEST real d7_opt_runScript.py scalers = %s" % json.dumps(sc, sort_keys=True))
        print("SELFTEST real d7_opt_runScript.py U0       = %r"
              % rr["module_constants"].get("U0"))
        expect = {"patchV": 0.1, "shape": 10.0, "twist": 0.1}
        # NOT a registered constant -- a PLANT (L-325): a value known to exist,
        # confirming the parser can express the names it is asked about.
        print("  PLANT: parser must return the three names it is asked about  %s"
              % ("PASS" if sc == expect else "FAIL"))
        (ok if sc == expect else fail).append("plant/real-runscript-scalers")
        print("  PLANT: U0 read from the source, not typed here              %s"
              % ("PASS" if rr["module_constants"].get("U0") == 291.6 else "FAIL"))
        (ok if rr["module_constants"].get("U0") == 291.6 else fail).append("plant/real-U0")
    else:
        print("  REFUSE: d7_opt_runScript.py found at NEITHER candidate path; "
              "the real-source plant did not run and this selftest is "
              "therefore INCOMPLETE (L-302)")
        fail.append("plant/real-runscript-NOT-FOUND")

    print("\nD7FR_LOCUS_SELFTEST %d/%d PASS" % (len(ok), len(ok) + len(fail)))
    if fail:
        print("FAILED: %s" % ", ".join(fail))
        return 1
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gate", metavar="WORKDIR")
    ap.add_argument("--runscript", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.gate:
        sys.stderr.write("usage: d7fr_endpoint_locus.py --selftest | "
                         "--gate <workdir> [--runscript P] [--out F]\n")
        return 64
    rs = a.runscript or os.path.join(a.gate, "d7_opt_runScript.py")
    try:
        res = gate(a.gate, rs)
    except LocusRefusal as e:
        sys.stderr.write("D7FR_LOCUS REFUSE %s\n" % e)
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
