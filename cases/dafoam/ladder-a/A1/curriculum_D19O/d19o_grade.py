#!/usr/bin/env python3
r"""Curriculum D19O -- THE FROZEN COMPARATOR.  Reads artefacts; runs no solver.

    d19o_grade.py --root <run root> --out <grade json>
    d19o_grade.py --selftest

===========================================================================
I. THE ONE SENTENCE THIS ITEM CANNOT SUPPORT, ENFORCED IN CODE
===========================================================================
**THIS ITEM CAN NEVER PUBLISH `PASS`.**  Not on either row, not at item level,
whatever every gate returns.  `VERDICT_CEILING = "GATE REACHED"` is applied by
`_apply_ceiling()` as the LAST step of composition, and `G-PROV` REFUSES (exit 2)
if the ceiling has been removed or widened.

The reason is `DAFOAM_CHARTER.md` section 1, this lab's own bright line:

  > *A DAFoam gradient is not a result until a finite-difference table stands
  > beside it at a step proved to lie in the plateau.*

**THE COMPRESSIBLE SINGLE-POINT GRADIENT HAS NO GRADED VERDICT AT ALL, AND ITS
PLATEAU DID NOT CLOSE.**  Both re-measured at this freeze:

  * `CURRICULUM-D19R` phase 1 ran clean -- `MESH X2 S8 N2 S1 R1` all rc=0,
    chain_rc 0, 12.416 core-min -- and **its grader REFUSED, rc=2, emitting no
    verdict**.  Its successor `CURRICULUM-D19R2`'s grading attempt 1 also
    returned **NOT A RESULT** (refusal `G19R-1h`).
  * `.../CURRICULUM-D19R-.../d19r_selected_step.json`: `all_two_sided = false`,
    `score_pct = 21.060684242435336`, `binding = ["shape[7]", "CD", "fine"]`.

So an optimisation on this ground inherits an **UNVERIFIED GRADIENT**.  It is
still worth buying -- the optimiser is the only instrument that can say whether
the compressible adjoint DRIVES A DESCENT on this case, and nothing else on the
ladder answers that -- but its headline verdict must not imply a plateau that
did not close.  The ceiling is how that is enforced rather than asked for.

===========================================================================
II. `shape[7]` IS A REGISTERED NON-RESULT, AND IT IS NOT RESCUABLE
===========================================================================
`G-PLAT7` sets `shape[7]/CD` to `NOT A RESULT` **from the registered list in
`d19o_xf.EXCLUDED_FROM_AGGREGATE`, never from the measured value.**  At s* on
D19R's own np=1 arm it agrees with the adjoint to **1.65155 %** -- INSIDE the
5 % band -- and it is excluded anyway, because what is missing is not agreement
but the PROOF that the estimate at s* is trustworthy, and that proof is the
plateau.  A selftest leg drives a `shape[7]` row that PASSES every band and
requires the gate to return `NOT A RESULT` regardless.

Its reading is PUBLISHED beside the aggregate, never instead of it
(`DAFOAM_CHARTER.md` section 3), and the aggregate's own key is named
`aggregate_pct_excl_flagged` so no reader can take it for an all-component one.

===========================================================================
III. WHAT THIS COMPARATOR REFUSES, AND WHAT IT MERELY GRADES
===========================================================================
**A REFUSAL IS `NOT A RESULT`, NEVER A DEGRADED VERDICT, AND IT EXITS 2.**
It refuses on a MALFORMED artefact and on a broken provenance.  It **NEVER**
refuses on an ABSENT one: D6 registered a chain stop as a meaningful outcome and
its grader refused with ZERO gate readings because one arm carried no ledger row,
leaving 2,257.933 core-min of real optimisation behind an instrument that could
not read it (L-322).  Here an absent arm is a **census reading** that `G-STAGES`
gates on, and every arm that ran is graded.

**NO `assert` STATEMENT APPEARS ANYWHERE IN THIS FILE.**  `python3 -O` strips
them, so an assert is not a guard (L-332).  `count_asserts()` proves it and is
itself proved against a planted assert.

**NO KEY IS FOUND BY A RECURSIVE HUNT.**  Every nested location is an explicit
path.  A reader that goes looking until it finds something will always find
something.

**`GCI` / Roache triple gating: NO GRID TRIPLE IS REGISTERED.**  This is a
single-grid optimisation on A1's own 4,032-cell mesh.  `CLAUDE.md` rule 5 has no
row to act on here, and this comparator says so rather than leaving a reader to
infer it from an absence.
"""
import argparse
import ast
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d19o_xf as XF                                              # noqa: E402
import d19o_age_guard as AGE                                      # noqa: E402
import d19o_stall as STALL                                        # noqa: E402

ITEM = "D19O"
VOCAB = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")

# ---- THE CEILING.  See the module docstring, part I. -------------------------
VERDICT_CEILING = "GATE REACHED"
CEILING_REASON = (
    "The compressible single-point gradient this optimisation spends has NO "
    "GRADED VERDICT (D19R's grader refused rc=2; D19R2 grading attempt 1 = NOT A "
    "RESULT) and its plateau did NOT close (all_two_sided=false, "
    "score_pct=21.060684242435336, binding=[shape[7],CD,fine]).  "
    "DAFOAM_CHARTER.md section 1: a gradient is not a result until an FD table "
    "stands beside it at a step PROVED to lie in the plateau.  This item "
    "therefore cannot publish PASS on any row or at item level, whatever its "
    "gates return.  REGISTERED BEFORE THE RUN.")

# ---- the declared program ----------------------------------------------------
ARMS_DECLARED = ["MESH", "O-S", "XE-S", "FE-S", "O-P", "XE-P", "FE-P"]
N_DECLARED = len(ARMS_DECLARED)
ARM_ROW = {"MESH": "SHIPPED", "O-S": "SHIPPED", "XE-S": "SHIPPED", "FE-S": "SHIPPED",
           "O-P": "PATCHED", "XE-P": "PATCHED", "FE-P": "PATCHED"}
ARM_RANKS = {a: 1 for a in ARMS_DECLARED}          # np = 1 ON EVERY ARM
ARM_KIND = {"MESH": "SCRIPT", "O-S": "O", "O-P": "O",
            "XE-S": "XE", "XE-P": "XE", "FE-S": "FE", "FE-P": "FE"}
TERMINAL = {"O": "D19O_O_WRITTEN", "XE": "D19O_X_WRITTEN", "FE": "D19O_F_WRITTEN"}
ARTEFACT = {"O": "d19o_O.json", "XE": "d19o_X.json", "FE": "d19o_F.json"}

# ---- THE REGISTERED CAP TABLE (PREREGISTRATION.md section 12) -----------------
# Caps are CEILINGS.  Predictions are ESTIMATES.  They are different numbers and
# the rule-12 ratio is taken against the PREDICTION, never against the cap.
CAPS = {"MESH": 5.0, "O-S": 40.0, "O-P": 40.0,
        "XE-S": 10.0, "XE-P": 10.0, "FE-S": 20.0, "FE-P": 20.0}
PREDICTED_CORE_MIN = {"MESH": 0.20, "O-S": 7.57, "O-P": 7.57,
                      "XE-S": 1.40, "XE-P": 1.40, "FE-S": 2.98, "FE-P": 2.98}
ITEM_CEILING_CORE_MIN = sum(CAPS.values())         # ASSERTED as the sum, never restated
CAP_MARGIN_S = 180                                 # the C-188 cap frame
RATE_USD_PER_CORE_H = 0.0513
COST_BASIS = ("c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER 2026-08-21/22, "
              "NOT MEASURED -- this box cannot read its own billing "
              "(COMPUTE_BUDGET_CHARTER.md section 5).  Core-minutes ARE measured, "
              "from this item's own ledger rows (wall_s x ranks / 60).")

# ---- registered placement and toolchain --------------------------------------
CPUSET_REGISTERED = "11"
MESH_CELLS = 4032
DIGEST = {"PATCHED": "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35",
          "SHIPPED": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"}
SO_MD5 = {"PATCHED": "85f59e87253e0a71a813f64ca6e4c425",
          "SHIPPED": "f0fcb488e0e98156575cd19548e91663"}

# ---- the registered intermediate threshold (DAFOAM_CHARTER.md section 9) ------
# A cap-stopped or stall-stopped optimiser is GATE REACHED only where this was
# met; otherwise NOT A RESULT.  Never PASS, and never described by the size of
# the improvement it reached.
MIN_DRAG_REDUCTION_PCT = 2.0
MIN_MAJORS_TO_HAVE_SEARCHED = 5

# ---- the travelling provenance (G-PROV) --------------------------------------
# Every link is read on disk at grade time.  An item verdict that leans on an
# upstream reading carries that reading with it or it publishes nothing.
PROV_CHAIN = [
    {"link": "CURRICULUM-D19R",
     "relation": "DIRECT -- the compressible FD plateau sweep this optimisation's "
                 "step and components come from",
     "item_verdict": "NOT A RESULT",
     "why": "its grader REFUSED rc=2 and emitted no verdict",
     "basis": "/home/ubuntu/certonomous-runs/CURRICULUM-D19R-a1-naca0012-subsonic-"
              "plateau/d19r_selected_step.json",
     "must_contain": '"all_two_sided": false'},
    {"link": "CURRICULUM-D19R2",
     "relation": "INHERITED -- the re-grade built to give D19R a verdict",
     "item_verdict": "NOT A RESULT",
     "why": "grading attempt 1 refused at G19R-1h (MANIFEST_ENTRY_MUTATED on "
            "system/decomposeParDict, an np>1 artefact); no grade JSON written",
     "basis": os.path.join(HERE, "..", "curriculum_D19R2", "RESULTS.md"),
     "must_contain": "NOT A RESULT"},
]

FATAL_TOKENS = ("Traceback (most recent call last)", "MPI_ABORT", "Segmentation fault",
                "std::bad_alloc", "PETSC ERROR", "Killed")
# Benign lines that are COUNTED AND NAMED, never silently suppressed.  A
# suppression a reader cannot see is the same defect wearing the other hat.
BENIGN = {"simple_no_criteria": "SIMPLE: no convergence criteria found",
          "continuity_errors": "time step continuity errors",
          "trapfpe_notice": "trapFpe:"}

_LEDGER = re.compile(
    r"^ARM=(?P<arm>\S+)\s+ROW=(?P<row>\S+)\s+IMG=(?P<img>\S+)\s+DIGEST=(?P<digest>\S+)\s+"
    r"rc=(?P<rc>-?\d+)\s+wall_s=(?P<wall>\d+)\s+ranks=(?P<ranks>\d+)\s+"
    r"core_min=(?P<core_min>[0-9.]+)\s+cap_core_min=(?P<cap>[0-9.]+).*?"
    r"cpuset=(?P<cpuset>\S+)", re.M)


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail},
                             sort_keys=True, default=str))


def md5_of(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def count_asserts(path):
    """L-332: `python3 -O` strips `assert`, so an assert is not a guard.  This
    counts them in a file.  It is itself proved against a PLANTED assert in the
    selftest -- a zero from a reader never shown a non-zero is not evidence."""
    return sum(1 for n in ast.walk(ast.parse(open(path).read()))
               if isinstance(n, ast.Assert))


def dig(doc, path, default=None):
    """An EXPLICIT tuple path.  Never a recursive hunt."""
    cur = doc
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list) and isinstance(k, int) and 0 <= k < len(cur):
            cur = cur[k]
        else:
            return default
    return cur


def _f(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# ============================================================================
# READERS
# ============================================================================
def read_ledger(root):
    p = os.path.join(root, "ledger.txt")
    if not os.path.isfile(p):
        return {}, []
    text = open(p, errors="replace").read()
    rows = {}
    order = []
    for m in _LEDGER.finditer(text):
        arm = m.group("arm")
        rows[arm] = {"arm": arm, "row": m.group("row"), "image": m.group("img"),
                     "digest": m.group("digest"), "rc": int(m.group("rc")),
                     "wall_s": int(m.group("wall")), "ranks": int(m.group("ranks")),
                     "core_min": _f(m.group("core_min")), "cap": _f(m.group("cap")),
                     "cpuset": m.group("cpuset")}
        order.append(arm)
    # the .so md5 the LOADING PROCESS printed, per arm
    for arm in rows:
        rows[arm]["so_md5"] = None
    for line in text.splitlines():
        m = re.match(r"^D19O_G9_(OK|REFUSE) arm=(\S+).*?libidwarp_so_md5=(\S+)", line)
        if m and m.group(2) in rows:
            rows[m.group(2)]["so_md5"] = m.group(3)
    return rows, order


def read_arm_log(root, arm):
    """The newest `<ARM>_*.log`, by name.  Deterministic, not a glob race."""
    cands = sorted(f for f in os.listdir(root)
                   if f.startswith(arm + "_") and f.endswith(".log"))
    if not cands:
        return None, ""
    p = os.path.join(root, cands[-1])
    return p, open(p, errors="replace").read()


def load_artefact(root, arm):
    """Returns (doc, path) or (None, path).  An ABSENT artefact is a CENSUS
    reading and returns None; a MALFORMED one REFUSES."""
    kind = ARM_KIND[arm]
    if kind == "SCRIPT":
        return None, None
    p = os.path.join(root, arm, ARTEFACT[kind])
    if not os.path.isfile(p):
        return None, p
    try:
        return json.load(open(p)), p
    except Exception as exc:                                      # noqa: BLE001
        refuse("ARTEFACT_MALFORMED", {"path": p, "error": repr(exc)[:300]})


# ============================================================================
# GATES
# ============================================================================
def g_prov():
    """The travelling chain.  REFUSES (exit 2) if it cannot be read, if any link
    is missing its basis, or if the verdict ceiling has been removed."""
    if VERDICT_CEILING not in VOCAB:
        refuse("G-PROV", {"verdict_ceiling_outside_vocabulary": VERDICT_CEILING})
    if VERDICT_CEILING == "PASS":
        refuse("G-PROV", {"verdict_ceiling_widened_to_PASS": CEILING_REASON})
    links = []
    for spec in PROV_CHAIN:
        basis = os.path.abspath(spec["basis"])
        exists = os.path.isfile(basis)
        contains = False
        if exists:
            txt = open(basis, errors="replace").read()
            contains = spec["must_contain"] in txt
        if not exists or not contains:
            refuse("G-PROV", {"link": spec["link"], "basis": basis,
                              "basis_exists": exists,
                              "basis_carries_%r" % spec["must_contain"]: contains,
                              "note": "an item that leans on an upstream reading "
                                      "carries that reading or publishes nothing"})
        if spec["item_verdict"] not in VOCAB:
            refuse("G-PROV", {"link": spec["link"],
                              "verdict_outside_vocabulary": spec["item_verdict"]})
        links.append({**spec, "basis": basis, "basis_exists": True,
                      "basis_carries_marker": True})
    return {"verdict": "SATISFIED", "n_links": len(links), "links": links,
            "verdict_ceiling": VERDICT_CEILING, "ceiling_reason": CEILING_REASON}


def g_stages(ran):
    """DECLARED vs EXECUTED as a GATE INPUT, not a footnote.  W3 logged 20 blocked
    stages of 33 perfectly, in two agreeing artefacts, and nothing read them."""
    short = N_DECLARED - len(ran)
    return {"declared": N_DECLARED, "executed": len(ran), "short": short,
            "arms_declared": ARMS_DECLARED, "arms_ran": sorted(ran),
            "arms_missing": [a for a in ARMS_DECLARED if a not in ran],
            "verdict": "PASS" if short == 0 else "NOT A RESULT"}


def g_completion(root, arm, led, doc):
    """CLAUDE.md rule 4, all of it or none of it: rc = 0, terminal statement, no
    fatal token, and the AGE GUARD.  Benign lines are COUNTED AND NAMED."""
    out = {"arm": arm, "clauses": {}}
    out["clauses"]["rc_zero"] = bool(led and led["rc"] == 0)
    lp, text = read_arm_log(root, arm)
    out["log"] = os.path.basename(lp) if lp else None
    kind = ARM_KIND[arm]
    if kind == "SCRIPT":
        out["clauses"]["terminal_statement"] = bool("D19O_MESH_IDENTITY_ALL_OK" in text)
    else:
        out["clauses"]["terminal_statement"] = bool(TERMINAL[kind] in text)
        out["clauses"]["artefact_present"] = doc is not None
    low = text.lower()
    hits = [t for t in FATAL_TOKENS if t.lower() in low]
    out["clauses"]["no_fatal_token"] = not hits
    out["fatal_tokens_seen"] = hits
    out["benign_counts"] = {k: low.count(v.lower()) for k, v in BENIGN.items()}
    out["_benign_note"] = ("COUNTED AND NAMED, never suppressed.  `SIMPLE: no "
                           "convergence criteria found` is OpenFOAM's banner and is "
                           "NOT evidence: DAFoam applies its own primalMinResTol.  "
                           "`trapFpe:` is an ENABLEMENT notice, not a crash.")
    # ---- the age guard --------------------------------------------------------
    ag = {"ran": False}
    mpath = os.path.join(root, arm, ".d19o_manifest.json")
    spath = AGE.sentinel_path(root, arm)
    if os.path.isfile(mpath) and os.path.isfile(spath):
        arts = [ARTEFACT[kind]] if kind != "SCRIPT" else ["checkMesh.log"]
        try:
            ev = AGE.check_arm(os.path.join(root, arm), arts, spath,
                               json.load(open(mpath)), [root])
            ag = {"ran": True, "ok": True, "evidence": ev}
        except AGE.Refusal as exc:
            d = json.loads(str(exc))
            ag = {"ran": True, "ok": False, "refusal": d}
            # THE REGISTERED FALSIFIER of the np=1 premise.  See section 5 of the
            # pre-registration: if this fires on `system/decomposeParDict`, np=1
            # did NOT prevent the D19R2 mutation, and that is a MEASUREMENT.  The
            # guard is NOT weakened after the fact.
            if (d.get("REFUSE") == "MANIFEST_ENTRY_MUTATED"
                    and "decomposeParDict" in str(d.get("detail", ""))):
                ag["np1_premise_falsified"] = True
    out["age_guard"] = ag
    out["clauses"]["age_guard"] = bool(ag.get("ok"))
    out["verdict"] = "PASS" if all(out["clauses"].values()) else "GATE FAIL"
    return out


def g_np(led_rows):
    """np = 1 on every arm.  A CONDITION ON THE INHERITANCE, not a setting."""
    bad = {a: r["ranks"] for a, r in led_rows.items() if r["ranks"] != ARM_RANKS.get(a, 1)}
    return {"registered": ARM_RANKS, "violations": bad,
            "verdict": "PASS" if not bad else "GATE FAIL",
            "why": "DAFOAM_CHARTER.md section 5 forbids carrying an FD reference "
                   "across np; A4 measured a 16,600x spread between two "
                   "decompositions of one mesh.  np=1 ALSO makes D19R2's "
                   "MANIFEST_ENTRY_MUTATED blocker unreachable, because "
                   "decomposePar never runs."}


def g9_toolchain(led_rows):
    bad = []
    for a, r in led_rows.items():
        want_row = ARM_ROW.get(a)
        if r["row"] != want_row:
            bad.append({"arm": a, "field": "row", "got": r["row"], "want": want_row})
        if r["digest"] != DIGEST.get(want_row):
            bad.append({"arm": a, "field": "digest", "got": r["digest"],
                        "want": DIGEST.get(want_row)})
        if r["so_md5"] != SO_MD5.get(want_row):
            bad.append({"arm": a, "field": "libidwarp_so_md5", "got": r["so_md5"],
                        "want": SO_MD5.get(want_row)})
    return {"registered_digests": DIGEST, "registered_so_md5": SO_MD5,
            "mismatches": bad, "verdict": "PASS" if not bad else "GATE FAIL",
            "why": "DAFOAM_CHARTER.md section 6: toolchain identity is an image "
                   "digest and a library hash, NEVER a version string.  All three "
                   "images report DAFoam 5.0.0."}


def g12_placement(led_rows):
    bad = {a: r["cpuset"] for a, r in led_rows.items() if r["cpuset"] != CPUSET_REGISTERED}
    return {"registered_cpuset": CPUSET_REGISTERED, "violations": bad,
            "verdict": "PASS" if not bad else "GATE FAIL",
            "delivered_cores_floor_composed": False,
            "_floor_note": "At np = 1 an overlapping cpuset costs wall time and "
                           "could not fail this gate, so the delivered-cores floor "
                           "is NOT COMPOSED and is registered as not composed.  The "
                           "sampler's reading is still published as a number."}


def g10_caps(led_rows):
    per, total = {}, 0.0
    over = []
    for a, r in led_rows.items():
        cm = r["core_min"] or 0.0
        total += cm
        pred = PREDICTED_CORE_MIN.get(a)
        per[a] = {"core_min": cm, "cap": CAPS.get(a), "predicted": pred,
                  "ratio_actual_over_predicted": (cm / pred) if pred else None,
                  "over_cap": bool(CAPS.get(a) is not None and cm > CAPS[a])}
        if per[a]["over_cap"]:
            over.append(a)
    # ITEM_CEILING is Sigma(CAPS), asserted here rather than restated by hand.
    ceiling_ok = abs(ITEM_CEILING_CORE_MIN - sum(CAPS.values())) < 1e-9
    if not ceiling_ok:
        refuse("G10", {"item_ceiling": ITEM_CEILING_CORE_MIN,
                       "sum_of_caps": sum(CAPS.values())})
    return {"per_arm": per, "total_core_min": round(total, 4),
            "item_ceiling_core_min": ITEM_CEILING_CORE_MIN,
            "item_point_prediction_core_min": round(sum(PREDICTED_CORE_MIN.values()), 4),
            "arms_over_cap": over,
            "total_over_ceiling": bool(total > ITEM_CEILING_CORE_MIN),
            "usd_derived_not_measured": round(total / 60.0 * RATE_USD_PER_CORE_H, 6),
            "cost_basis": COST_BASIS,
            "ratio_actual_over_predicted_item":
                round(total / sum(PREDICTED_CORE_MIN.values()), 4)
                if sum(PREDICTED_CORE_MIN.values()) else None,
            "verdict": "PASS" if (not over and total <= ITEM_CEILING_CORE_MIN)
                       else "GATE FAIL",
            "_cap_vs_prediction": "Caps are CEILINGS; predictions are ESTIMATES.  The "
                                  "rule-12 ratio is taken against the PREDICTION, "
                                  "never against the cap."}


def g_mesh(root):
    p = os.path.join(root, "MESH", "checkMesh.log")
    if not os.path.isfile(p):
        return {"verdict": "NOT A RESULT", "cells": None, "registered": MESH_CELLS,
                "note": "no checkMesh.log -- the MESH arm did not run"}
    m = re.search(r"^\s*cells:\s*(\d+)\s*$", open(p, errors="replace").read(), re.M)
    cells = int(m.group(1)) if m else None
    return {"cells": cells, "registered": MESH_CELLS,
            "verdict": "PASS" if cells == MESH_CELLS else "GATE FAIL"}


def g_designpoint(root, arms_ran):
    """The endpoint arms were evaluated AT THE OPTIMUM, and at THEIR OWN row's
    optimum.  `DAFOAM_CHARTER.md` section 9: the FD check is at the FINAL design
    point, not only at the baseline."""
    out = {"per_arm": {}, "verdict": "PASS"}
    for arm in arms_ran:
        kind = ARM_KIND[arm]
        if kind not in ("XE", "FE"):
            continue
        row = ARM_ROW[arm]
        o_arm = "O-S" if row == "SHIPPED" else "O-P"
        xo_p = os.path.join(root, o_arm, XF.XOPT)
        doc, _ = load_artefact(root, arm)
        rec = {"expects": xo_p, "xopt_present": os.path.isfile(xo_p)}
        if not rec["xopt_present"] or doc is None:
            rec["ok"] = False
        else:
            xo = json.load(open(xo_p))
            dp = dig(doc, ("design_point",), {})
            rec["row_match"] = (xo.get("row") == row == doc.get("row"))
            rec["shape_match"] = (dp.get("shape") == xo.get("shape"))
            rec["patchV_match"] = (dp.get("patchV") == xo.get("patchV"))
            rec["not_baseline"] = any(_f(v, 0.0) != 0.0 for v in (dp.get("shape") or []))
            rec["ok"] = bool(rec["row_match"] and rec["shape_match"] and rec["patchV_match"])
            rec["_not_baseline_note"] = (
                "`not_baseline` is REPORTED, NEVER GATED: an optimiser that "
                "legitimately converges at the baseline would otherwise be failed "
                "for succeeding.  What IS gated is that the endpoint arm read its "
                "OWN row's d19o_xopt.json and used those exact bytes.")
        out["per_arm"][arm] = rec
        if not rec.get("ok"):
            out["verdict"] = "GATE FAIL"
    return out


def g_noopt_endpoint(root, arms_ran):
    """No optimiser ran in an endpoint arm.  An `opt_IPOPT.txt` under XE/FE means
    the endpoint moved, and the gradient would not be at the point it names."""
    bad = []
    for arm in arms_ran:
        if ARM_KIND[arm] not in ("XE", "FE"):
            continue
        for ev in ("opt_IPOPT.txt", "OptView.hst"):
            if os.path.exists(os.path.join(root, arm, ev)):
                bad.append({"arm": arm, "optimiser_evidence": ev})
        doc, _ = load_artefact(root, arm)
        if doc is not None and doc.get("no_optimiser_ran") is not True:
            bad.append({"arm": arm, "artefact_does_not_declare": "no_optimiser_ran"})
    return {"violations": bad, "verdict": "PASS" if not bad else "GATE FAIL"}


def g_evalfail(root, arms_ran):
    """A failed evaluation is WRITTEN, not omitted.  An F arm that silently writes
    fewer rows and calls itself complete is what this gate exists to catch."""
    out = {"per_arm": {}, "verdict": "PASS"}
    n_comp = len(XF.COMPONENTS)
    n_steps = len(XF.FD_STEPS_ENDPOINT["shape"]) + 1        # + the trivial baseline
    declared_expected = n_comp * n_steps * 2 + 2            # + baseline and repeat
    out["evals_declared_expected"] = declared_expected
    out["_census_arithmetic"] = ("%d components x %d steps (3 decade + 1 trivial "
                                 "baseline) x 2 signs + 2 baselines = %d"
                                 % (n_comp, n_steps, declared_expected))
    for arm in arms_ran:
        if ARM_KIND[arm] != "FE":
            continue
        doc, _ = load_artefact(root, arm)
        if doc is None:
            out["per_arm"][arm] = {"artefact": "ABSENT"}
            continue
        d = doc.get("evaluations_declared")
        rec = {"declared": d, "failed": doc.get("evaluations_failed"),
               "failures": doc.get("evaluation_failures"),
               "matches_census": (d == declared_expected)}
        out["per_arm"][arm] = rec
        if not rec["matches_census"]:
            out["verdict"] = "GATE FAIL"
    return out


def g_opt9(root, row, arms_ran):
    """`DAFOAM_CHARTER.md` section 9, per row.

    PASS is reachable from this gate ONLY where IPOPT printed its OWN convergence
    statement.  It is then still capped by `_apply_ceiling`.  A cap-, budget- or
    stall-stopped run is GATE REACHED where the registered intermediate threshold
    was met and NOT A RESULT otherwise -- never PASS, and never described by the
    size of the improvement it reached."""
    arm = "O-S" if row == "SHIPPED" else "O-P"
    if arm not in arms_ran:
        return {"arm": arm, "verdict": "NOT A RESULT", "why": "arm did not run"}
    doc, _ = load_artefact(root, arm)
    if doc is None:
        return {"arm": arm, "verdict": "NOT A RESULT", "why": "no d19o_O.json"}
    printed = doc.get("ipopt_printed_convergence") is True
    exit_text = doc.get("ipopt_exit")
    rows_n = doc.get("ipopt_table_rows") or 0
    red = _f(doc.get("drag_reduction_pct"))
    stall = doc.get("stall") or {}
    stalled = bool(stall.get("A"))
    met = bool(red is not None and red >= MIN_DRAG_REDUCTION_PCT
               and rows_n >= MIN_MAJORS_TO_HAVE_SEARCHED)
    if printed:
        verdict = "PASS"
        why = "IPOPT printed its OWN convergence statement: %r" % exit_text
    elif met:
        verdict = "GATE REACHED"
        why = ("stopped without a convergence statement (exit=%r, stall_A=%s) and the "
               "REGISTERED intermediate threshold was met: %.4f %% >= %.1f %% over "
               "%d majors >= %d" % (exit_text, stalled, red, MIN_DRAG_REDUCTION_PCT,
                                    rows_n, MIN_MAJORS_TO_HAVE_SEARCHED))
    else:
        verdict = "NOT A RESULT"
        why = ("stopped without a convergence statement (exit=%r) and the registered "
               "intermediate threshold was NOT met (reduction=%r over %d majors)"
               % (exit_text, red, rows_n))
    return {"arm": arm, "verdict": verdict, "why": why,
            "ipopt_exit": exit_text, "ipopt_printed_convergence": printed,
            "ipopt_table_rows": rows_n, "ipopt_n_iterations": doc.get("ipopt_n_iterations"),
            "max_iter_registered": XF.MAX_MAJORS,
            "reached_iteration_cap": bool(rows_n >= XF.MAX_MAJORS),
            "stall_condition_A": stall.get("A"),
            "stall_condition_B_state": stall.get("condition_B_state"),
            "drag_reduction_pct": red,
            "CD_baseline_trimmed": doc.get("CD_baseline_trimmed"),
            "CD_final": doc.get("CD_final"),
            "CL_baseline_trimmed": doc.get("CL_baseline_trimmed"),
            "CL_final": doc.get("CL_final"), "CL_target": doc.get("CL_target"),
            "_cl_travels": "The CL pair travels with EVERY drag number this item "
                           "publishes.  A drag reduction at an unstated CL is not a "
                           "reportable number.",
            "_improvement_grades_nothing":
                "DAFOAM_CHARTER.md section 9 forbids grading an optimisation by the "
                "size of its improvement.  `drag_reduction_pct` is reported and is "
                "an input to the REGISTERED intermediate threshold only.",
            "registered_intermediate_threshold_pct": MIN_DRAG_REDUCTION_PCT,
            "registered_min_majors": MIN_MAJORS_TO_HAVE_SEARCHED}


def _adj_lookup(xdoc, of_key):
    a = dig(xdoc, ("adjoint", of_key), {}) or {}
    out = {}
    for dv in ("shape", "patchV"):
        for i, v in enumerate(a.get(dv, []) or []):
            out[(dv, i)] = _f(v)
    return out


def g_fd(root, row, arms_ran):
    """Band D per component, band E on the aggregate, and the DECADE plateau --
    all AT THE FINAL DESIGN POINT, and all with `shape[7]` EXCLUDED BY NAME."""
    xe = "XE-S" if row == "SHIPPED" else "XE-P"
    fe = "FE-S" if row == "SHIPPED" else "FE-P"
    out = {"xe_arm": xe, "fe_arm": fe,
           "excluded_from_aggregate": [list(c) for c in XF.EXCLUDED_FROM_AGGREGATE],
           "excluded_from_aggregate_reason": XF.EXCLUSION_REASON,
           "band_D_pct": XF.FD_BAND_PCT, "band_E_pct": XF.AGG_BAND_PCT,
           "plateau_tol_pct": XF.PLATEAU_TOL_PCT}
    if xe not in arms_ran or fe not in arms_ran:
        out.update({"verdict": "NOT A RESULT",
                    "why": "an endpoint arm did not run (%s ran=%s, %s ran=%s)"
                           % (xe, xe in arms_ran, fe, fe in arms_ran)})
        return out
    xdoc, _ = load_artefact(root, xe)
    fdoc, _ = load_artefact(root, fe)
    if xdoc is None or fdoc is None:
        out.update({"verdict": "NOT A RESULT", "why": "an endpoint artefact is absent"})
        return out

    adj_cd, adj_cl = _adj_lookup(xdoc, "CD"), _adj_lookup(xdoc, "CL")
    pairs_cd, pairs_cl = [], []
    per = {}
    for r in fdoc.get("rows", []):
        if r.get("status") != "MEASURED":
            continue
        dv, idx = r.get("dv"), r.get("idx")
        key = "%s[%s]" % (dv, idx)
        s_key = repr(XF.S_STAR[dv]) if dv in XF.S_STAR else None
        fd_at = (r.get("fd") or {}).get(s_key) if s_key else None
        excluded = XF.is_excluded(dv, idx)
        rec = {"excluded_from_aggregate": excluded,
               "registered_non_result": excluded,
               "plateau_CD": r.get("plateau_CD"), "plateau_CL": r.get("plateau_CL")}
        for of_key, adj, bag in (("CD", adj_cd, pairs_cd), ("CL", adj_cl, pairs_cl)):
            a = adj.get((dv, idx))
            f = _f((fd_at or {}).get("dCD" if of_key == "CD" else "dCL")) \
                if (fd_at and fd_at.get("ok")) else None
            e = XF.rel_pct(a, f)
            sign_flip = bool(a is not None and f is not None and a * f < 0)
            plat = r.get("plateau_%s" % of_key) or {}
            # THE REGISTERED NON-RESULT.  Set from the LIST, never from the value.
            if excluded:
                v = "NOT A RESULT"
            elif e is None:
                v = "NOT A RESULT"
            elif not plat.get("two_sided"):
                v = "NOT A RESULT"
            elif sign_flip or e > XF.FD_BAND_PCT:
                v = "GATE FAIL"
            else:
                v = "PASS"
            rec[of_key] = {"adjoint": a, "fd_at_s_star": f, "rel_pct": e,
                           "sign_flip": sign_flip,
                           "plateau_two_sided": plat.get("two_sided"),
                           "verdict": v}
            if not excluded and a is not None and f is not None:
                bag.append((a, f))
        per[key] = rec

    agg_cd = XF.aggregate_excl_flagged(pairs_cd)
    agg_cl = XF.aggregate_excl_flagged(pairs_cl)
    graded = [k for k, v in per.items() if not v["excluded_from_aggregate"]]
    fails = [k for k in graded if per[k]["CD"]["verdict"] == "GATE FAIL"
             or per[k]["CL"]["verdict"] == "GATE FAIL"]
    nars = [k for k in graded if per[k]["CD"]["verdict"] == "NOT A RESULT"
            or per[k]["CL"]["verdict"] == "NOT A RESULT"]

    if len(graded) < 4 or nars:
        verdict = "NOT A RESULT"
    elif fails or (agg_cd is not None and agg_cd > XF.AGG_BAND_PCT) \
            or (agg_cl is not None and agg_cl > XF.AGG_BAND_PCT):
        verdict = "GATE FAIL"
    else:
        verdict = "PASS"

    out.update({
        "per_component": per,
        "n_graded_components": len(graded),
        "graded_components": sorted(graded),
        "components_gate_fail": sorted(fails),
        "components_not_a_result": sorted(nars),
        "aggregate_pct_excl_flagged_CD": agg_cd,
        "aggregate_pct_excl_flagged_CL": agg_cl,
        "_aggregate_key_name": "The key says `excl_flagged` because the aggregate is "
                               "over FOUR components, not five.  shape[7] is EXCLUDED "
                               "BY NAME and its own reading is published above, beside "
                               "the aggregate and never instead of it "
                               "(DAFOAM_CHARTER.md section 3).",
        "harness_floor_pct": [2.5, 5.0],
        "_harness_floor": "VERIFICATION_CHARTER.md section 7 step 4: the harness-sound "
                          "floor on this stack is 2.5 to 5 %% vector-norm relative "
                          "error, and a number below that is a claim about the "
                          "harness.  REPORTED, NEVER GATED.",
        "verdict": verdict})
    return out


def g_plat7(fd_gate):
    """`shape[7]` is a REGISTERED NON-RESULT.  This gate re-states it as its own
    reading so it appears on the record even if a reader skips `g_fd`, and it is
    set FROM THE REGISTERED LIST -- never from the measured value."""
    per = fd_gate.get("per_component", {})
    recs = {}
    for dv, idx in XF.EXCLUDED_FROM_AGGREGATE:
        k = "%s[%d]" % (dv, idx)
        r = per.get(k, {})
        recs[k] = {"verdict": "NOT A RESULT",
                   "set_from": "REGISTERED LIST, never from the measured value",
                   "measured_CD": r.get("CD"), "measured_CL": r.get("CL"),
                   "plateau_CD": r.get("plateau_CD")}
    return {"components": recs, "verdict": "NOT A RESULT",
            "why": XF.EXCLUSION_REASON,
            "_cannot_be_rescued": "At s* on D19R's np=1 arm this component agrees with "
                                  "the adjoint to 1.65155 %, INSIDE band D.  It is "
                                  "excluded anyway: what is missing is not agreement "
                                  "but the PROOF that the estimate at s* is "
                                  "trustworthy, and that proof is the plateau."}


def g_tb(root, row, arms_ran):
    """`DAFOAM_CHARTER.md` section 4: the same probe at a DELIBERATELY WRONG step.
    If the wrong step also passes, the gate is not measuring what it claims and
    the row's FD verdict is WITHDRAWN to NOT A RESULT.

    A probe that ERRORED counts as FAILING the baseline -- an unevaluable estimate
    is not a pass."""
    fe = "FE-S" if row == "SHIPPED" else "FE-P"
    out = {"fe_arm": fe, "step": XF.TB_STEP, "max_passing": XF.TB_MAX_PASSING,
           "_why_this_step": "five orders below s*.  On a CD derivative of order "
                             "1e-2 the FD numerator at 1e-8 is ~1e-10, at or below "
                             "the MEASURED primal repeatability on this case at "
                             "np=1 (eta_used = 9.652218954658842e-11, D19R S1).  The "
                             "estimate is noise and MUST fail band D."}
    if fe not in arms_ran:
        out.update({"verdict": "NOT A RESULT", "why": "the FE arm did not run"})
        return out
    fdoc, _ = load_artefact(root, fe)
    xe = "XE-S" if row == "SHIPPED" else "XE-P"
    xdoc, _ = load_artefact(root, xe)
    if fdoc is None or xdoc is None:
        out.update({"verdict": "NOT A RESULT", "why": "an endpoint artefact is absent"})
        return out
    adj = _adj_lookup(xdoc, "CD")
    passing, rows = [], {}
    for r in fdoc.get("rows", []):
        if r.get("status") != "MEASURED":
            continue
        dv, idx = r.get("dv"), r.get("idx")
        if XF.is_excluded(dv, idx):
            continue
        row_tb = (r.get("fd") or {}).get(repr(XF.TB_STEP))
        k = "%s[%s]" % (dv, idx)
        if not row_tb or not row_tb.get("ok"):
            rows[k] = {"evaluable": False, "passes_band_D": False,
                       "note": "a probe that errored counts as FAILING the baseline"}
            continue
        e = XF.rel_pct(adj.get((dv, idx)), _f(row_tb.get("dCD")))
        p = bool(e is not None and e <= XF.FD_BAND_PCT)
        rows[k] = {"evaluable": True, "rel_pct": e, "passes_band_D": p}
        if p:
            passing.append(k)
    out.update({"per_component": rows, "n_passing": len(passing),
                "components_passing": sorted(passing),
                "verdict": "PASS" if len(passing) <= XF.TB_MAX_PASSING else "GATE FAIL",
                "withdraws_row_fd_verdict": bool(len(passing) > XF.TB_MAX_PASSING)})
    return out


# ============================================================================
# COMPOSITION
# ============================================================================
def _apply_ceiling(verdict):
    """THE LAST STEP OF EVERY COMPOSITION.  See the module docstring, part I.
    `PASS` becomes the ceiling; every other token passes through unchanged, so
    the ceiling can only make a verdict WORSE and never better."""
    order = {"PASS": 6, "GATE REACHED": 5, "PENDING": 4, "BLOCKED": 3,
             "GATE FAIL": 2, "NOT A RESULT": 1}
    if order.get(verdict, 0) > order.get(VERDICT_CEILING, 0):
        return VERDICT_CEILING, True
    return verdict, False


def compose_row(row, gates):
    opt = gates["G-OPT9"][row]["verdict"]
    fd = gates["G5_fd"][row]["verdict"]
    tb = gates["G-TB"][row]["verdict"]
    if gates["G-TB"][row].get("withdraws_row_fd_verdict"):
        fd = "NOT A RESULT"
    # A row whose OPTIMISER is NOT A RESULT cannot be rescued by any other gate.
    if opt == "NOT A RESULT":
        raw, why = "NOT A RESULT", "the optimiser verdict is NOT A RESULT"
    elif "NOT A RESULT" in (fd, tb):
        raw, why = "NOT A RESULT", "an endpoint gate is NOT A RESULT (fd=%s tb=%s)" % (fd, tb)
    elif "GATE FAIL" in (opt, fd, tb):
        raw, why = "GATE FAIL", "a gate failed (opt=%s fd=%s tb=%s)" % (opt, fd, tb)
    elif opt == "GATE REACHED":
        raw, why = "GATE REACHED", "the optimiser stopped without its own convergence statement"
    else:
        raw, why = "PASS", "every gate passed"
    # THE ENDPOINT FD CAN ONLY MAKE THINGS WORSE, NEVER BETTER.  An endpoint PASS
    # never upgrades a GATE REACHED optimiser.  Registered before the run.
    final, capped = _apply_ceiling(raw)
    return {"row": row, "verdict": final, "verdict_before_ceiling": raw,
            "capped_by_ceiling": capped, "why": why,
            "optimiser": opt, "endpoint_fd": fd, "trivial_baseline": tb}


def compose_item(gates, rows):
    stages = gates["G-STAGES"]["verdict"]
    rvs = [rows[r]["verdict"] for r in rows]
    hard = [gates[g]["verdict"] for g in
            ("G-M2_mesh_identity", "G-NP", "G9_toolchain", "G10_caps",
             "G12_placement", "G-DESIGNPOINT", "G-NOOPT-ENDPOINT", "G-EVALFAIL")]
    if stages == "NOT A RESULT" or "NOT A RESULT" in rvs:
        raw = "NOT A RESULT"
    elif stages == "BLOCKED":
        raw = "BLOCKED"
    elif "GATE FAIL" in rvs or "GATE FAIL" in hard:
        raw = "GATE FAIL"
    elif "GATE REACHED" in rvs:
        raw = "GATE REACHED"
    else:
        raw = "PASS"
    final, capped = _apply_ceiling(raw)
    if final not in VOCAB:
        refuse("VOCAB", {"composed_verdict_outside_the_fixed_vocabulary": final})
    return final, raw, capped


def grade(root):
    prov = g_prov()
    led_rows, _order = read_ledger(root)
    arms_ran = [a for a in ARMS_DECLARED if a in led_rows]

    gates = {"G-PROV": prov, "G-STAGES": g_stages(arms_ran)}
    gates["G-M2_mesh_identity"] = g_mesh(root)
    gates["G-NP"] = g_np(led_rows)
    gates["G9_toolchain"] = g9_toolchain(led_rows)
    gates["G12_placement"] = g12_placement(led_rows)
    gates["G10_caps"] = g10_caps(led_rows)
    gates["G-DESIGNPOINT"] = g_designpoint(root, arms_ran)
    gates["G-NOOPT-ENDPOINT"] = g_noopt_endpoint(root, arms_ran)
    gates["G-EVALFAIL"] = g_evalfail(root, arms_ran)

    comp = {}
    for arm in ARMS_DECLARED:
        if arm not in led_rows:
            comp[arm] = {"arm": arm, "verdict": "NOT RUN"}
            continue
        doc, _ = load_artefact(root, arm)
        comp[arm] = g_completion(root, arm, led_rows[arm], doc)
    gates["G1_completion"] = comp

    gates["G-OPT9"] = {r: g_opt9(root, r, arms_ran) for r in ("SHIPPED", "PATCHED")}
    gates["G5_fd"] = {r: g_fd(root, r, arms_ran) for r in ("SHIPPED", "PATCHED")}
    gates["G-TB"] = {r: g_tb(root, r, arms_ran) for r in ("SHIPPED", "PATCHED")}
    gates["G-PLAT7"] = {r: g_plat7(gates["G5_fd"][r]) for r in ("SHIPPED", "PATCHED")}
    gates["G6_dot_product_duality"] = {
        "verdict": "NOT MEASURED",
        "why": "AV-2 measured that seeding forward mode makes the primal FAIL on "
               "this exact case on BOTH images.  Named, never composed."}
    gates["GCI_roache"] = {
        "verdict": "NOT APPLICABLE",
        "why": "No grid triple is registered: this is a single-grid optimisation on "
               "A1's own 4,032-cell mesh.  CLAUDE.md rule 5 has no row to act on "
               "here, and this comparator says so rather than leaving a reader to "
               "infer it from an absence."}

    rows = {r: compose_row(r, gates) for r in ("SHIPPED", "PATCHED")}
    verdict, raw, capped = compose_item(gates, rows)

    # THE CEILING BINDS AT ROW LEVEL AND THE ITEM INHERITS, so `capped` at item
    # level is normally False even when the ceiling did all the work.  A reader
    # of the item record must not have to reconstruct that, so it is stated:
    # `capped_by_ceiling_anywhere` is True if the ceiling bound EITHER row or the
    # item.  Without it, an item record could read `capped_by_ceiling: false`
    # beside a GATE REACHED that only exists BECAUSE of the ceiling -- which is
    # the shape of a true field that leaves a false impression.
    capped_anywhere = bool(capped or any(rows[r]["capped_by_ceiling"] for r in rows))

    return {
        "item": ITEM, "root": os.path.abspath(root),
        "grader_md5": md5_of(os.path.abspath(__file__)),
        "verdict": verdict, "verdict_before_ceiling": raw,
        "capped_by_ceiling": capped,
        "capped_by_ceiling_anywhere": capped_anywhere,
        "rows_capped_by_ceiling": [r for r in rows if rows[r]["capped_by_ceiling"]],
        "verdict_ceiling": VERDICT_CEILING, "verdict_ceiling_reason": CEILING_REASON,
        "verdict_statement":
            "%s -- %s.  THIS ITEM CANNOT PUBLISH PASS: it spends a compressible "
            "gradient with NO GRADED VERDICT whose plateau did not close "
            "(shape[7]/CD one-sided at 21.060684242435336 %%), and shape[7] is a "
            "REGISTERED NON-RESULT excluded by name from every aggregate."
            % (verdict, "two rows: SHIPPED=%s PATCHED=%s"
               % (rows["SHIPPED"]["verdict"], rows["PATCHED"]["verdict"])),
        "rows": rows, "gates": gates,
        "vocabulary": list(VOCAB),
        "asserts_in_grader": count_asserts(os.path.abspath(__file__)),
        "submissions": "PARKED -- nothing in this item is filed, sent, uploaded, "
                       "registered, posted or commented outside this box "
                       "(CLAUDE.md rule 7; DAFOAM_CHARTER.md section 10).",
    }


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)      # MANDATORY: the driver names it,
    ap.add_argument("--selftest", action="store_true")   # not the comparator
    a = ap.parse_args(argv)
    try:
        out = grade(a.root)
    except Refusal as exc:
        sys.stderr.write("D19O_GRADE REFUSED: %s\n" % exc)
        return 2
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.flush()
        os.fsync(fh.fileno())
    sys.stdout.write("D19O_GRADE_WRITTEN %s verdict=%s rows=%s\n"
                     % (a.out, out["verdict"],
                        {r: out["rows"][r]["verdict"] for r in out["rows"]}))
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        import d19o_grade_selftest as ST
        sys.exit(ST.main())
    sys.exit(main(sys.argv[1:]))
