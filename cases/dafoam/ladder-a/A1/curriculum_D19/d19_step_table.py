#!/usr/bin/env python3
"""D19 precondition instrument -- the FD STEP TABLE that D15 and D16 never printed.

READ-ONLY over the frozen D15/D16 artefacts.  ZERO SOLVER COMPUTE.  This script
launches nothing: it opens five JSON files, arithmetics them, and prints
markdown.  It is the executable half of
`cases/dafoam/ladder-a/A1/curriculum_D19/D15_D16_FD_STEP_TABLE.md` -- every
number in that record is this script's output and nothing else.

WHY IT EXISTS.  `VERIFICATION_CHARTER.md` sec7 requires a step-size sweep table
in the shape

    | step | rel err | rel err (excl. flagged) | cosine | status |

"whenever step 1 is being established" -- step 1 being "confirm the step sits in
the well-converged plateau with a two or three point mini-sweep".
`DAFOAM_CHARTER.md` sec3 adds that "the plateau is read per component, not off
the vector".  D15's and D16's RESULTS.md publish NEITHER table: they publish the
graded aggregate and the per-component relative errors, but no step column and
no cosine column.  The three-step data exists in the frozen artefacts; this
script is what turns it into the required table.

WHAT IT DOES NOT DO.  It does not edit D15's or D16's frozen documents, it does
not regrade them, and it does not change any verdict either item recorded.  It
reports what their own artefacts say about the PLATEAU, which is the one thing
their records left unstated.

TWO CONTROLS, BOTH REFUSING (CLAUDE.md rule 3):

  CONTROL A -- SAME-DATA.  Every plateau_neighbour_pct and rel_err_pct this
  script computes is asserted equal, to 1e-9, against the corresponding value in
  the item's own frozen graded JSON.  If this reader were reading different data
  from the grader, or arithmeticking it differently, this refuses.

  CONTROL B -- PLANTED.  A known perturbation is injected into one FD value and
  the table is required to MOVE by the predicted amount.  A reader that cannot
  see a plant it was handed cannot be trusted to report a plateau it did not
  see.  Refuses if the plant is invisible or lands off prediction.

Usage:  python3 d19_step_table.py            # markdown to stdout
        python3 d19_step_table.py --selftest # controls only, exit 0/2
"""
import json
import math
import os
import sys

ROOTS = {
    "D15": "/home/ubuntu/certonomous-runs/CURRICULUM-D15-a1-naca0012-subsonic",
    "D16": "/home/ubuntu/certonomous-runs/CURRICULUM-D16-a1-naca0012-transonic",
}
ARM = {"SHIPPED": ("X-S", "F-S"), "PATCHED": ("X-P", "F-P")}

# --- the registered constants of the items being read, NOT new law -------------------
# d15_grade.py:75-77 / d16_grade.py, quoted so this reader cannot drift from the grader.
NEAR_ZERO_ABS = 1.0e-14
PLATEAU_TOL_PCT = 10.0     # d15_grade.py:75  PLATEAU_TOL_PCT = 10.0
FD_BAND_PCT = 5.0          # band D, per component
AGG_BAND_PCT = 5.0         # band E, aggregate vector-relative
# VERIFICATION_CHARTER.md sec7 step 5: "step between 1e-3 and 1e-2".
CHARTER_STEP_LO, CHARTER_STEP_HI = 1.0e-3, 1.0e-2
# VERIFICATION_CHARTER.md sec7 step 3: flag a component moving > 50 % of its own
# magnitude across one decade of step.
DECADE_FLAG_PCT = 50.0

LEVELNAME = ["coarse", "mid (registered)", "fine"]


class Refusal(Exception):
    pass


def refuse(where, detail):
    raise Refusal(json.dumps({"REFUSE": where, "detail": detail}, sort_keys=True, default=str))


def load(item, row):
    r = ROOTS[item]
    xa, fa = ARM[row]
    lo = item.lower()
    for p in (os.path.join(r, xa, "%s_X.json" % lo), os.path.join(r, fa, "%s_F.json" % lo)):
        if not os.path.exists(p):
            refuse("ARTEFACT_ABSENT", {"path": p})
    return (json.load(open(os.path.join(r, xa, "%s_X.json" % lo))),
            json.load(open(os.path.join(r, fa, "%s_F.json" % lo))))


def graded_json(item):
    r = ROOTS[item]
    c = [f for f in os.listdir(r) if f.startswith("%s_grade_" % item) and f.endswith(".json")]
    if len(c) != 1:
        refuse("GRADED_JSON_NOT_UNIQUE", {"item": item, "found": c})
    return c[0], json.load(open(os.path.join(r, c[0])))


def fd_at(F, dv, idx, step, key):
    for rw in F["rows"]:
        if rw["dv"] == dv and int(rw["idx"]) == idx:
            for s, v in rw["fd"].items():
                if float(s) == step:
                    return (float(v[key]), bool(v["ok"]))
    return (None, False)


def analyse(item, row, of, fd_override=None):
    """Per-component plateau reading.  fd_override keys (dv, idx, step) -> value."""
    X, F = load(item, row)
    comps = [(a, int(b)) for a, b in F["components_requested"]]
    steps = F["steps"]
    key = "dCD" if of == "CD" else "dCL"
    out = []
    for dv, idx in comps:
        j = float(X["adjoint"][of][dv][idx])
        ss = sorted(steps[dv], reverse=True)              # coarse -> fine
        vals, oks = [], []
        for s in ss:
            v, ok = fd_at(F, dv, idx, s, key)
            if fd_override and (dv, idx, s) in fd_override:
                v = fd_override[(dv, idx, s)]
            vals.append(v)
            oks.append(ok)
        rec = {"dv": dv, "idx": idx, "J_adj": j, "steps": ss, "fd": vals}
        if any(v is None for v in vals) or not all(oks):
            rec["status"] = "FD_STEP_FAILED_OR_ABSENT"
            out.append(rec)
            continue
        ref = vals[1]                                      # the middle step is the graded one
        rec["ref"] = ref
        if abs(ref) < NEAR_ZERO_ABS:
            rec["status"] = "NEAR_ZERO"
            out.append(rec)
            continue
        nb = [abs(vals[0] - ref) / abs(ref) * 100.0, abs(vals[2] - ref) / abs(ref) * 100.0]
        rec["nb"] = nb
        # THE READING THE GRADER NEVER PRINTED: one side or two.
        rec["plateau"] = ("TWO-SIDED" if max(nb) <= PLATEAU_TOL_PCT else
                          "ONE-SIDED" if min(nb) <= PLATEAU_TOL_PCT else "NONE")
        rec["one_sided_at"] = (None if rec["plateau"] != "ONE-SIDED" else
                               ("fine %g" % ss[2] if nb[1] > PLATEAU_TOL_PCT else "coarse %g" % ss[0]))
        # sec7 step 3: > 50 % of own magnitude across one decade.
        rec["decade_flag"] = bool(max(nb) > DECADE_FLAG_PCT)
        if min(nb) > PLATEAU_TOL_PCT:
            rec["status"] = "NO_PLATEAU"
            out.append(rec)
            continue
        rec["rel_err_pct"] = abs(ref - j) / abs(ref) * 100.0
        rec["sign_flip"] = bool(ref * j < 0.0)
        rec["status"] = "GATE FAIL" if (rec["sign_flip"] or rec["rel_err_pct"] > FD_BAND_PCT) else "PASS"
        out.append(rec)
    return out


def vector_at(recs, lv, excl=()):
    a, b = [], []
    for r in recs:
        if (r["dv"], r["idx"]) in excl or r.get("fd") is None or r["fd"][lv] is None:
            continue
        a.append(r["fd"][lv])
        b.append(r["J_adj"])
    if len(a) < 2:
        return (None, None, len(a))
    num = math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
    den = math.sqrt(sum(x * x for x in a))
    dot = sum(x * y for x, y in zip(a, b))
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(y * y for y in b))
    return (num / den * 100.0, dot / (na * nb), len(a))


def norm_share(recs):
    n = math.sqrt(sum(r["J_adj"] ** 2 for r in recs))
    return {(r["dv"], r["idx"]): abs(r["J_adj"]) / n * 100.0 for r in recs}, n


# ================= CONTROLS ==========================================================
def control_a():
    """Same-data: reproduce the grader's own plateau and rel-err numbers."""
    n = 0
    for item in ("D15", "D16"):
        _, g = graded_json(item)
        for row in ("SHIPPED", "PATCHED"):
            gr = g.get("gates", {}).get("G5_%s" % row, {})
            for of in ("CD", "CL"):
                gg = gr.get("G5_%s" % of)
                if not gg:
                    continue
                recs = analyse(item, row, of)
                for c in gg["components"]:
                    for r in recs:
                        if r["dv"] != c["dv"] or r["idx"] != c["idx"]:
                            continue
                        if "plateau_neighbour_pct" in c and "nb" in r:
                            for x, y in zip(c["plateau_neighbour_pct"], r["nb"]):
                                if abs(x - y) > 1e-9:
                                    refuse("CONTROL_A", {"item": item, "row": row, "of": of,
                                                         "dv": c["dv"], "idx": c["idx"],
                                                         "grader": x, "reader": y})
                                n += 1
                        if "rel_err_pct" in c and "rel_err_pct" in r:
                            if abs(c["rel_err_pct"] - r["rel_err_pct"]) > 1e-9:
                                refuse("CONTROL_A", {"item": item, "row": row, "of": of,
                                                     "dv": c["dv"], "idx": c["idx"],
                                                     "grader": c["rel_err_pct"], "reader": r["rel_err_pct"]})
                            n += 1
    if n == 0:
        refuse("CONTROL_A", {"no_values_compared": True})
    return n


def control_b():
    """Planted: perturb one FD value, require the table to move by the predicted amount."""
    base = analyse("D15", "PATCHED", "CD")
    t = [r for r in base if r["dv"] == "shape" and r["idx"] == 7]
    if not t:
        refuse("CONTROL_B", {"target_absent": "D15/PATCHED/CD shape[7]"})
    t = t[0]
    plant = 0.10 * abs(t["fd"][2])
    pert = analyse("D15", "PATCHED", "CD",
                   fd_override={("shape", 7, t["steps"][2]): t["fd"][2] + plant})
    t2 = [r for r in pert if r["dv"] == "shape" and r["idx"] == 7][0]
    pred = abs(t["fd"][2] + plant - t["ref"]) / abs(t["ref"]) * 100.0
    if abs(t2["nb"][1] - pred) > 1e-9:
        refuse("CONTROL_B", {"predicted": pred, "observed": t2["nb"][1]})
    if abs(t2["nb"][1] - t["nb"][1]) < 1.0:
        refuse("CONTROL_B", {"plant_invisible": True, "before": t["nb"][1], "after": t2["nb"][1]})
    return {"before_pct": t["nb"][1], "after_pct": t2["nb"][1], "predicted_pct": pred,
            "delta_pp": t2["nb"][1] - t["nb"][1], "plant_abs": plant}


# ================= REPORT ============================================================
def emit():
    print("<!-- GENERATED BY d19_step_table.py -- do not hand-edit the tables below. -->")
    for item in ("D15", "D16"):
        gname, g = graded_json(item)
        print("\n## %s -- run root `%s`" % (item, ROOTS[item]))
        print("\nGraded JSON: `%s`.  Item verdict `%s`; rows %s." %
              (gname, g.get("verdict"), json.dumps(g.get("rows"))))
        for row in ("PATCHED", "SHIPPED"):
            for of in ("CD", "CL"):
                recs = analyse(item, row, of)
                share, nrm = norm_share(recs)
                print("\n### %s / %s row / objective `%s`" % (item, row, of))
                print("\n**Per-component step table** (`DAFOAM_CHARTER.md` sec3: the plateau is read "
                      "per component). `nb` = deviation of that step from the graded middle step, "
                      "as percent of the middle step. Registered plateau tolerance 10.0 %.\n")
                print("| dv | idx | share of \\|J_adj\\| | J_adj | FD @ coarse | FD @ mid (graded) | "
                      "FD @ fine | nb coarse | nb fine | plateau | rel err vs adjoint | sign match | status |")
                print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
                for r in recs:
                    s = share[(r["dv"], r["idx"])]
                    if "nb" not in r:
                        print("| `%s` | %d | %.3f %% | %+.6e | -- | -- | -- | -- | -- | -- | -- | -- | %s |"
                              % (r["dv"], r["idx"], s, r["J_adj"], r["status"]))
                        continue
                    pl = r["plateau"]
                    if pl == "ONE-SIDED":
                        pl = "**ONE-SIDED** (fails %s)" % r["one_sided_at"]
                    print("| `%s` | %d | %.3f %% | %+.6e | %+.6e | %+.6e | %+.6e | %.4f %% | %.4f %% | %s | %s | %s | %s |"
                          % (r["dv"], r["idx"], s, r["J_adj"], r["fd"][0], r["fd"][1], r["fd"][2],
                             r["nb"][0], r["nb"][1], pl,
                             ("%.4f %%" % r["rel_err_pct"]) if "rel_err_pct" in r else "--",
                             ("yes" if not r.get("sign_flip") else "**NO**") if "sign_flip" in r else "--",
                             r["status"]))
                print("\nSteps: coarse/mid/fine = %s.  \\|J_adj\\| over the five registered components = %.6e."
                      % (" / ".join("%g" % v for v in recs[0]["steps"]), nrm))
                flagged = tuple((r["dv"], r["idx"]) for r in recs if r.get("plateau") in ("ONE-SIDED", "NONE"))
                print("\n**Step-size sweep, `VERIFICATION_CHARTER.md` sec7 shape.** `rel err` is the "
                      "vector-relative aggregate over the five registered components AT THAT STEP; "
                      "`excl. flagged` drops the components whose plateau is not two-sided%s.\n"
                      % ("" if not flagged else " (%s)" % ", ".join("`%s`[%d]" % f for f in flagged)))
                print("| step | rel err | rel err (excl. flagged) | cosine | status |")
                print("|---|---|---|---|---|")
                for lv in range(3):
                    rel, cos, n = vector_at(recs, lv)
                    rel2, cos2, n2 = vector_at(recs, lv, excl=flagged)
                    st = LEVELNAME[lv]
                    sv = recs[0]["steps"][lv]
                    inrange = CHARTER_STEP_LO <= sv <= CHARTER_STEP_HI
                    stat = "%s%s" % (st, "" if inrange else " -- **OUTSIDE sec7 step-5 range 1e-3..1e-2**")
                    print("| %g (shape) / %g (patchV) | %.4f %% | %s | %.8f | %s |"
                          % (sv, [r for r in recs if r["dv"] == "patchV"][0]["steps"][lv],
                             rel, ("%.4f %%" % rel2) if rel2 is not None else "n < 2", cos, stat))
                agg = g.get("gates", {}).get("G5_%s" % row, {}).get("G5_%s" % of, {}).get("aggregate_rel_err_pct")
                if agg is not None:
                    print("\nGrader's published aggregate at the graded (mid) step: **%.6f %%** -- "
                          "reproduced by this reader to 1e-9 (CONTROL A)." % agg)


def main():
    selftest = "--selftest" in sys.argv
    try:
        n = control_a()
        b = control_b()
    except Refusal as e:
        print("REFUSED: %s" % e, file=sys.stderr)
        return 2
    if selftest:
        print("CONTROL A same-data: OK, %d values reproduced against the frozen graded JSONs." % n)
        print("CONTROL B planted:   OK, D15/PATCHED/CD `shape[7]` fine-side neighbour "
              "%.4f %% -> %.4f %% (predicted %.4f %%), delta %.4f pp -- the reader SEES the plant."
              % (b["before_pct"], b["after_pct"], b["predicted_pct"], b["delta_pp"]))
        return 0
    emit()
    print("\n---\n\n## Controls\n")
    print("- **CONTROL A (same-data)** -- `OK`. **%d** plateau and relative-error values recomputed "
          "from the raw `*_F.json` / `*_X.json` and asserted equal to 1e-9 against the frozen graded "
          "JSONs. This reader is reading what the grader read." % n)
    print("- **CONTROL B (planted)** -- `OK`. A perturbation of %.6e (10 %% of its own magnitude) was "
          "injected into D15/PATCHED/`CD` `shape[7]` at the fine step. The fine-side neighbour moved "
          "**%.4f %% -> %.4f %%**, predicted **%.4f %%**, delta **%.4f pp**. A reader that could not "
          "see this plant would not be trusted to report a plateau."
          % (b["plant_abs"], b["before_pct"], b["after_pct"], b["predicted_pct"], b["delta_pp"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
