#!/usr/bin/env python3
"""FADR grader -- DAFoam's shipped forward-AD regression, two toolchain rows.

WHAT THIS IS
------------
An INDEPENDENT reimplementation of upstream's `testFuncs.reg_file_comp`
comparison, run on the PRESERVED RAW output of each arm.  It is independent on
purpose: the shipped comparator REWRITES the file it compares (it writes the
reference line over any produced line that matched), so a grader that trusted
the post-comparison file would be reading the reference back to itself.  The
gate is still upstream's exit code, recorded per arm by the driver; this grader
reproduces it and refuses if the two disagree.

INSTRUMENT RULES OBSERVED HERE, EACH PAID FOR BY A MEASURED FAILURE
-------------------------------------------------------------------
* No `assert` carries a refusal, a guard, a control or a gate (L-332).
  `python3 -O` deletes every assert.  Every refusal is `raise` or
  `sys.exit(2)`, and `--selftest` parses this file's own AST and refuses if a
  single `ast.Assert` node exists.
* No unconditional success print.  Every PASS/MATCH/CONTROL-SEEN line is
  emitted from inside the branch that verified it.
* A zero needs a live planted control (standing rule 3).  `--selftest` plants
  a mismatch, a match, an empty read, a short read and both sides of the
  tolerance disjunction, requires each to be SEEN, then MUTATES the predicate
  and requires the controls to FLIP.

EXIT CODES
----------
    0   graded; verdicts printed (the verdict itself may be GATE FAIL --
        a graded failure is a successful grading)
    2   refusal, or selftest failure, or the AST check failed
    1   usage error
"""
from __future__ import annotations

import argparse
import ast
import json
import math
import os
import re
import sys
from pathlib import Path

VALUE_RE = re.compile(r"^@value\s+(\S+)\s+(\S+)\s+(\S+)\s*$")
KEY_RE = re.compile(r"^Dictionary Key:\s*(.+?)\s*$")

EXPECTED_VALUES = 24          # 2 functions x 6 dv entries x {Adjoint, ForwardAD}
ARMS = ("S", "P")
ROW_IMAGE = {
    "S": ("dafoam/opt-packages:latest",
          "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc"),
    "P": ("dafoam-idwarp-rot:v1",
          "sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"),
}
# Registered in PREREGISTRATION.md section 7.  Not editable post-compute.
P5_BAND = 1.0e-5
P4_BAND = 1.0e-8

# The predicate mutation switch used by --selftest control C3.  Production runs
# never set it; the selftest sets it and REQUIRES the controls to flip.
_MUTATE = os.environ.get("FADR_MUTATE_PREDICATE", "") == "1"


class Refusal(Exception):
    """A condition that must stop the instrument under ANY interpreter flag."""


def close_enough(ref_val: float, cmp_val: float, rel_tol: float, abs_tol: float) -> bool:
    """Upstream's disjunction, reimplemented: rel_err < rel_tol OR abs_err < abs_tol."""
    denom = cmp_val if cmp_val != 0.0 else 1e-16
    rel_err = abs((ref_val - cmp_val) / denom)
    abs_err = abs(ref_val - cmp_val)
    if _MUTATE:
        return not (abs_err < abs_tol or rel_err < rel_tol)
    return abs_err < abs_tol or rel_err < rel_tol


def parse_value_file(path: Path) -> tuple[list[tuple[str, float, float, float]], int]:
    """Return [(qualified_key, value, rel_tol, abs_tol)] and the raw @value count.

    The qualified key is '<function>/<dvkey>' built from the nesting of
    'Dictionary Key:' lines that upstream's reg_write_dict emits: an outer key
    per function, an inner key per '<dv><index>-{Adjoint,ForwardAD}'.
    """
    if not path.is_file():
        raise Refusal(f"ABSENT: {path} does not exist -- nothing to grade")
    text = path.read_text(errors="replace").splitlines()
    outer = None
    pending_key = None
    out: list[tuple[str, float, float, float]] = []
    n_values = 0
    for line in text:
        mk = KEY_RE.match(line)
        if mk:
            key = mk.group(1)
            # A function key is followed by another Dictionary Key before any
            # @value; a dv key is followed immediately by an @value.
            if pending_key is not None:
                outer = pending_key
            pending_key = key
            continue
        mv = VALUE_RE.match(line)
        if mv:
            n_values += 1
            if pending_key is None:
                raise Refusal(f"MALFORMED: @value with no preceding key in {path}")
            qual = f"{outer}/{pending_key}" if outer else pending_key
            out.append((qual, float(mv.group(1)), float(mv.group(2)), float(mv.group(3))))
            pending_key = None
    return out, n_values


def compare(ref_path: Path, cmp_path: Path, expected: int = EXPECTED_VALUES) -> dict:
    """Independent reimplementation of reg_file_comp.  Refuses on a silent read."""
    ref, n_ref = parse_value_file(ref_path)
    cmp_, n_cmp = parse_value_file(cmp_path)
    if n_cmp == 0:
        raise Refusal(
            f"SILENT-EMPTY (control C4): {cmp_path} carries ZERO @value lines. "
            "A reader that saw nothing must never report agreement -- the mphys "
            "forward hooks are a silent no-op that warns and falls through."
        )
    if n_ref != expected:
        raise Refusal(f"REFERENCE COUNT: {ref_path} has {n_ref} @value lines, expected {expected}")
    if n_cmp != n_ref:
        raise Refusal(
            f"COUNT MISMATCH (control C5): produced {n_cmp} @value lines against "
            f"{n_ref} in the reference. Refused, never padded."
        )
    rows = []
    n_bad = 0
    for (kr, vr, rt, at), (kc, vc, _, _) in zip(ref, cmp_):
        if kr != kc:
            raise Refusal(f"KEY ORDER: reference key {kr!r} against produced {kc!r}")
        ok = close_enough(vr, vc, rt, at)
        denom = vc if vc != 0.0 else 1e-16
        rows.append({
            "key": kr, "ref": vr, "got": vc, "rel_tol": rt, "abs_tol": at,
            "rel_err": abs((vr - vc) / denom), "abs_err": abs(vr - vc),
            "governed_by": "abs_tol" if abs(vr) * rt < at else "rel_tol",
            "match": ok,
        })
        if not ok:
            n_bad += 1
    return {"n_values": n_cmp, "n_mismatch": n_bad, "match": n_bad == 0, "rows": rows}


def duality(rows: list[dict]) -> dict:
    """Adjoint vs ForwardAD relative disagreement, per function and dv entry.

    This is a DIAGNOSTIC reading (PREREGISTRATION.md section 7): it never moves
    a verdict.  It is the quantity the A1 NACA0012 observation put at 3.8 %.
    """
    got = {r["key"]: r["got"] for r in rows}
    gov = {r["key"]: r["governed_by"] for r in rows}
    pairs = {}
    for k in got:
        if k.endswith("-Adjoint"):
            fwd = k[: -len("-Adjoint")] + "-ForwardAD"
            if fwd in got:
                a, f = got[k], got[fwd]
                denom = a if a != 0.0 else 1e-16
                pairs[k[: -len("-Adjoint")]] = {
                    "adjoint": a, "forward": f,
                    "rel_disagreement": abs((a - f) / denom),
                    "governed_by": gov[k],
                }
    rel_governed = [v["rel_disagreement"] for v in pairs.values() if v["governed_by"] == "rel_tol"]
    return {
        "pairs": pairs,
        "n_pairs": len(pairs),
        "n_rel_governed": len(rel_governed),
        "worst_rel_governed": max(rel_governed) if rel_governed else None,
        "worst_all": max((v["rel_disagreement"] for v in pairs.values()), default=None),
    }


def grade_arm(arm_dir: Path, arm: str) -> dict:
    """Grade one toolchain row.  Returns a dict; never prints a verdict itself."""
    out: dict = {"arm": arm, "image": ROW_IMAGE[arm][0], "digest": ROW_IMAGE[arm][1],
                 "dir": str(arm_dir)}
    status_p = arm_dir / "ARM_STATUS.json"
    if not status_p.is_file():
        out["verdict"] = "BLOCKED"
        out["reason"] = f"no ARM_STATUS.json at {status_p}: the arm never reported"
        return out
    st = json.loads(status_p.read_text())
    out["mpirun_rc"] = st.get("mpirun_rc")
    out["comparator_rc"] = st.get("comparator_rc")
    out["docker_rc"] = st.get("docker_rc")
    out["wall_s"] = st.get("wall_s")
    out["primal_failure_banner"] = st.get("primal_failure_banner")

    raw = arm_dir / "DAFoam_Test_DASimpleFoamForward.RAW.txt"
    ref = arm_dir / "DAFoam_Test_DASimpleFoamForwardRef.txt"
    datum = arm_dir / "AGE_DATUM_runRegTests_DASimpleFoamForward.py"

    if not raw.is_file():
        out["verdict"] = "BLOCKED"
        out["reason"] = ("no raw output: the regression produced no @value lines. "
                         "If ARM_STATUS records a checkPrimalFailure banner, that is the "
                         "toolchain refusing the forward-seeded primal (branch P-B).")
        return out

    # Age datum, resolved BY EXISTENCE (PREREGISTRATION.md section 6).
    if not datum.is_file():
        out["verdict"] = "NOT A RESULT"
        out["reason"] = f"age datum absent: {datum}"
        return out
    out["age_datum_delta_s"] = raw.stat().st_mtime - datum.stat().st_mtime
    if out["age_datum_delta_s"] <= 0:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = ("AGE GUARD FIRED: the raw output is not newer than the harness "
                         f"that produced it (delta {out['age_datum_delta_s']:.1f} s)")
        return out

    try:
        cmpres = compare(ref, raw)
    except Refusal as exc:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = f"comparator refused: {exc}"
        return out

    out["n_values"] = cmpres["n_values"]
    out["n_mismatch"] = cmpres["n_mismatch"]
    # AMENDMENT 3 (v1.0c, 2026-08-27, PRE-COMPUTE, on the supervisor's order): the
    # DISCRIMINATING POWER of this gate travels beside every verdict, so a PASS can
    # never be oversold as 24 tight agreements.  Upstream's tolerance is a
    # DISJUNCTION (rel<1e-8 OR abs<1e-12), so abs_tol governs wherever |value|<1e-4.
    # These are counts of VALUES, not of Adjoint/ForwardAD PAIRS -- the pair count in
    # the duality block is half the value count and must never be read as this one.
    out["n_rel_governed_values"] = sum(1 for r in cmpres["rows"] if r["governed_by"] == "rel_tol")
    out["n_abs_governed_values"] = sum(1 for r in cmpres["rows"] if r["governed_by"] == "abs_tol")
    out["independent_match"] = cmpres["match"]
    out["mismatched_keys"] = [r["key"] for r in cmpres["rows"] if not r["match"]]
    out["duality"] = duality(cmpres["rows"])
    out["rows"] = cmpres["rows"]

    # The GATE is upstream's own exit code.  This grader reproduces it and
    # refuses if the two readings disagree -- a disagreement means one of the
    # two readers is wrong and neither may be believed.
    upstream_match = out["comparator_rc"] == 0
    if out["comparator_rc"] is None:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = "no comparator exit code was recorded for this arm"
        return out
    if upstream_match != cmpres["match"]:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = (f"READER DISAGREEMENT: upstream comparator rc={out['comparator_rc']} "
                         f"(match={upstream_match}) against this grader's independent "
                         f"match={cmpres['match']} over {cmpres['n_values']} values. "
                         "Neither reading is believed.")
        return out
    if out["mpirun_rc"] not in (0, None) and out["mpirun_rc"] != 0:
        out["verdict"] = "NOT A RESULT"
        out["reason"] = f"mpirun rc={out['mpirun_rc']} on a run that nonetheless emitted values"
        return out
    if cmpres["match"]:
        out["verdict"] = "PASS"
        out["reason"] = (f"{cmpres['n_values']}/{EXPECTED_VALUES} values inside upstream's own "
                         f"disjunction (rel<1e-8 OR abs<1e-12), read twice and agreeing -- "
                         f"of which {out['n_rel_governed_values']} are REL-GOVERNED (the tight "
                         f"agreements) and {out['n_abs_governed_values']} are ABS-GOVERNED, where "
                         f"1e-12 absolute is as loose as 8e-4 relative on the smallest value. "
                         f"This PASS is {out['n_rel_governed_values']} tight agreements, "
                         f"not {cmpres['n_values']}.")
    else:
        out["verdict"] = "GATE FAIL"
        out["reason"] = (f"{cmpres['n_mismatch']} of {cmpres['n_values']} values outside "
                         f"upstream's own tolerances: {out['mismatched_keys']} "
                         f"({out['n_rel_governed_values']} of the {cmpres['n_values']} values are "
                         f"REL-GOVERNED, {out['n_abs_governed_values']} ABS-GOVERNED)")
    return out


def score_predictions(arms: dict) -> list[dict]:
    """P1-P7 as frozen.  A prediction MISS never changes a verdict."""
    P = []
    s, p = arms.get("S", {}), arms.get("P", {})
    both = [a for a in (s, p) if a.get("verdict")]

    rcs = [a.get("comparator_rc") for a in (s, p)]
    P.append({"id": "P1", "text": "comparator exit code identical on both rows",
              "score": "HIT" if (rcs[0] is not None and rcs[0] == rcs[1]) else
                       ("MISS" if None not in rcs else "NOT_MEASURED"),
              "observed": f"S rc={rcs[0]}, P rc={rcs[1]}"})

    ns = [a.get("n_values") for a in (s, p)]
    P.append({"id": "P2", "text": f"exactly {EXPECTED_VALUES} @value lines per arm",
              "score": "HIT" if ns == [EXPECTED_VALUES, EXPECTED_VALUES] else
                       ("NOT_MEASURED" if None in ns else "MISS"),
              "observed": f"S {ns[0]}, P {ns[1]}"})

    banners = [a.get("primal_failure_banner") for a in (s, p)]
    P.append({"id": "P3", "text": "forward-seeded primal reaches acceptance (no checkPrimalFailure)",
              "score": "HIT" if banners == [False, False] else
                       ("NOT_MEASURED" if None in banners else "MISS"),
              "observed": f"S banner={banners[0]}, P banner={banners[1]}"})

    def shape_cd(a):
        d = a.get("duality", {}).get("pairs", {})
        for k, v in d.items():
            if k.endswith("/shape0") and "CD" in k:
                return v["rel_disagreement"]
        return None
    v4 = [shape_cd(a) for a in (s, p)]
    meas4 = [x for x in v4 if x is not None]
    P.append({"id": "P4", "text": f"CD shape0 Adjoint-vs-ForwardAD agreement better than {P4_BAND:g}",
              "score": "NOT_MEASURED" if not meas4 else
                       ("HIT" if max(meas4) < P4_BAND else "MISS"),
              "observed": f"S {v4[0]}, P {v4[1]}"})

    w5 = [a.get("duality", {}).get("worst_rel_governed") for a in (s, p)]
    meas5 = [x for x in w5 if x is not None]
    P.append({"id": "P5", "text": f"worst rel-governed duality disagreement below {P5_BAND:g} "
                                  "(the 3.8 % NACA0012 gap is NOT reproduced)",
              "score": "NOT_MEASURED" if not meas5 else
                       ("HIT" if max(meas5) < P5_BAND else "MISS"),
              "observed": f"S {w5[0]}, P {w5[1]}"})

    walls = [a.get("wall_s") for a in (s, p)]
    if None in walls:
        P.append({"id": "P6", "text": "chain cost inside [10, 120] core-min",
                  "score": "NOT_MEASURED", "observed": f"S {walls[0]} s, P {walls[1]} s"})
    else:
        cm = sum(walls) * 4.0 / 60.0
        P.append({"id": "P6", "text": "chain cost inside [10, 120] core-min",
                  "score": "HIT" if 10.0 <= cm <= 120.0 else "MISS",
                  "observed": f"{cm:.3f} core-min (wall {walls[0]:.0f}+{walls[1]:.0f} s at 4 ranks)"})

    if s.get("rows") and p.get("rows"):
        diffs = [(a["key"], a["got"], b["got"]) for a, b in zip(s["rows"], p["rows"])
                 if a["got"] != b["got"]]
        P.append({"id": "P7", "text": "S and P bit-identical on all 24 values",
                  "score": "HIT" if not diffs else "MISS",
                  "observed": "identical" if not diffs else f"{len(diffs)} differ: {diffs[:4]}"})
    else:
        P.append({"id": "P7", "text": "S and P bit-identical on all 24 values",
                  "score": "NOT_MEASURED", "observed": "one or both rows produced no values"})
    return P


def item_verdict(arms: dict) -> tuple[str, str]:
    """PASS only if BOTH rows PASS; otherwise the weakest row's label."""
    order = ["PASS", "GATE FAIL", "NOT A RESULT", "BLOCKED"]
    vs = [arms.get(a, {}).get("verdict", "BLOCKED") for a in ARMS]
    worst = max(vs, key=lambda v: order.index(v) if v in order else len(order))
    if all(v == "PASS" for v in vs):
        return "PASS", ("both rows PASS -- branch P-A: DAFoam's shipped forward-AD regression "
                        "passes in the image it ships in, and the A1 observation is CASE-DEPENDENCE")
    if worst in ("GATE FAIL", "BLOCKED"):
        return worst, ("branch P-B: DAFoam's own shipped forward-AD regression does NOT pass in "
                       "the image it ships in. Rows: " + ", ".join(f"{a}={arms.get(a,{}).get('verdict')}"
                                                                   for a in ARMS) +
                       ". Any upstream artefact is a DRAFT carrying NOT FILED at its head; "
                       "it is not filed, sent or posted anywhere (standing rule 7).")
    return worst, "rows: " + ", ".join(f"{a}={arms.get(a,{}).get('verdict')}" for a in ARMS)


# ----------------------------------------------------------------- selftest --

def _ast_has_assert(path: Path) -> bool:
    tree = ast.parse(path.read_text())
    return any(isinstance(n, ast.Assert) for n in ast.walk(tree))


REF_TEXT = "\n".join([
    "Dictionary Key: f",
    "Dictionary Key: a0-Adjoint",
    "@value         1.0000000000000000 1e-08 1e-12",
    "Dictionary Key: a0-ForwardAD",
    "@value         1.0000000000000000 1e-08 1e-12",
    "Dictionary Key: b0-Adjoint",
    "@value         0.0000000010000000 1e-08 1e-12",
    "Dictionary Key: b0-ForwardAD",
    "@value         0.0000000010000000 1e-08 1e-12",
]) + "\n"


def selftest(tmp: Path) -> int:
    fails: list[str] = []
    seen: list[str] = []
    here = Path(__file__).resolve()

    if _ast_has_assert(here):
        print("AST REFUSAL: this file contains an ast.Assert node; python3 -O would delete it")
        return 2
    seen.append("AST: 0 ast.Assert nodes in this file")

    ref = tmp / "ref.txt"
    ref.write_text(REF_TEXT)

    def run(name: str, comp_text: str, want: str) -> None:
        p = tmp / f"c_{name}.txt"
        p.write_text(comp_text)
        try:
            r = compare(ref, p, expected=4)
            got = "MATCH" if r["match"] else "MISMATCH"
        except Refusal as exc:
            got = "REFUSE"
            globals()["_last_refusal"] = str(exc)
        if got == want:
            seen.append(f"{name}: {got} as required")
        else:
            fails.append(f"{name}: got {got}, required {want}")

    # C2 -- the reader can see a MATCH (reference against itself)
    run("C2_match_identical", REF_TEXT, "MATCH")
    # C1 -- the reader can see a MISMATCH (a0 perturbed far beyond both tolerances)
    run("C1_mismatch_seen", REF_TEXT.replace("1.0000000000000000", "1.5000000000000000"), "MISMATCH")
    # C4 -- the silent-empty read REFUSES, never returns MATCH
    run("C4_silent_empty", "Dictionary Key: f\n", "REFUSE")
    # C5 -- a short read REFUSES, never pads
    run("C5_short_read", "\n".join(REF_TEXT.splitlines()[:-1]) + "\n", "REFUSE")
    # C6a -- a value passing ONLY on abs_tol is accepted (b0 = 1e-9 moved by 5e-13:
    #        rel_err 5e-4 fails rel_tol 1e-8, abs_err 5e-13 passes abs_tol 1e-12)
    run("C6a_abs_only_accepted",
        REF_TEXT.replace("0.0000000010000000", "0.0000000010005000"), "MATCH")
    # C6b -- the same value moved beyond abs_tol as well is rejected
    run("C6b_abs_exceeded_rejected",
        REF_TEXT.replace("0.0000000010000000", "0.0000000019999999"), "MISMATCH")
    # C6c -- a value passing ONLY on rel_tol is accepted (a0 = 1.0 moved by 1e-9:
    #        abs_err 1e-9 fails abs_tol 1e-12, rel_err 1e-9 passes rel_tol 1e-8)
    run("C6c_rel_only_accepted",
        REF_TEXT.replace("1.0000000000000000", "1.0000000010000000"), "MATCH")

    # C3 -- MUTATE the predicate and require the controls to FLIP.  The
    # all-bad file is read UNMUTATED first, so the flip is measured against a
    # reading taken by the same code path, not asserted.
    run("C3_premutation_all_bad",
        REF_TEXT.replace("1.0000000000000000", "1.5000000000000000")
                .replace("0.0000000010000000", "0.0000000050000000"), "MISMATCH")
    globals()["_MUTATE"] = True
    run("C3_mutated_match_flips", REF_TEXT, "MISMATCH")
    # every value moved beyond BOTH tolerances: unmutated MISMATCH, mutated MATCH.
    # (A partly-perturbed file cannot serve here: file-level match is the AND over
    # rows, so under inversion a mixed file stays MISMATCH and the control would
    # be untestable rather than passing.)
    all_bad = REF_TEXT.replace("1.0000000000000000", "1.5000000000000000") \
                      .replace("0.0000000010000000", "0.0000000050000000")
    run("C3_mutated_all_bad_flips", all_bad, "MATCH")
    globals()["_MUTATE"] = False
    run("C3_restored_match", REF_TEXT, "MATCH")

    # The duality reading must itself be shown able to see a non-zero.
    r = compare(ref, tmp / "c_C2_match_identical.txt", expected=4)
    d0 = duality(r["rows"])
    p = tmp / "c_plant.txt"
    p.write_text(REF_TEXT.replace(
        "Dictionary Key: a0-ForwardAD\n@value         1.0000000000000000 1e-08 1e-12",
        "Dictionary Key: a0-ForwardAD\n@value         1.0380000000000000 1e-08 1e-12"))
    dp = duality(compare(ref, p, expected=4)["rows"])
    w0 = d0["worst_all"]
    wp = dp["worst_all"]
    if w0 is not None and wp is not None and w0 == 0.0 and wp > 0.03:
        seen.append(f"DUALITY PLANT: reads 0.0 unplanted and {wp:.4f} with a 3.8 %-shaped plant")
    else:
        fails.append(f"DUALITY PLANT: unplanted {w0}, planted {wp} -- the reader was not shown a non-zero")

    for line in seen:
        print(f"  SEEN   {line}")
    for line in fails:
        print(f"  FAIL   {line}")
    print(f"units: {len(seen)} seen, {len(fails)} failed")
    if fails:
        return 2
    print("SELFTEST PASS -- every planted control was seen and the mutation flipped both directions")
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="FADR grader")
    ap.add_argument("--run-root", type=Path, help="run root holding S/ and P/")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json-out", type=Path)
    a = ap.parse_args(argv)

    if a.selftest:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            return selftest(Path(td))

    if a.run_root is None:
        print("usage: --run-root <dir> | --selftest", file=sys.stderr)
        return 1
    if not a.run_root.is_dir():
        print(f"REFUSAL: run root {a.run_root} does not exist", file=sys.stderr)
        return 2

    arms = {}
    for arm in ARMS:
        arms[arm] = grade_arm(a.run_root / arm, arm)

    preds = score_predictions(arms)
    verdict, why = item_verdict(arms)

    print("=" * 78)
    print("FADR -- DAFoam's shipped forward-AD regression, run UNMODIFIED, two rows")
    print("=" * 78)
    for arm in ARMS:
        r = arms[arm]
        print(f"\nROW {arm}  {r['image']}")
        print(f"  digest   {r['digest']}")
        print(f"  VERDICT  {r.get('verdict')}")
        print(f"  reason   {r.get('reason')}")
        if r.get("n_values") is not None:
            d = r.get("duality", {})
            print(f"  values   {r['n_values']} read, {r['n_mismatch']} outside tolerance")
            print(f"  POWER    {r['n_rel_governed_values']} of {r['n_values']} values are "
                  f"REL-GOVERNED (rel<1e-8); {r['n_abs_governed_values']} are ABS-GOVERNED "
                  f"(abs<1e-12, as loose as 8e-4 relative on the smallest). The verdict above "
                  f"rests on {r['n_rel_governed_values']} tight agreements, not {r['n_values']}.")
            print(f"  duality  {d.get('n_pairs')} PAIRS, {d.get('n_rel_governed')} of them "
                  f"rel-governed (PAIRS, not values -- half the POWER count above); "
                  f"worst rel-governed {d.get('worst_rel_governed')}, worst all {d.get('worst_all')}")
    print("\nPREDICTIONS (frozen; a MISS never changes a verdict)")
    for p in preds:
        print(f"  {p['id']}  {p['score']:<12} {p['text']}")
        print(f"        observed: {p['observed']}")
    print(f"\nITEM VERDICT: {verdict}")
    print(f"  {why}")

    if a.json_out:
        a.json_out.write_text(json.dumps(
            {"arms": arms, "predictions": preds, "item_verdict": verdict, "why": why},
            indent=2, default=str))
        print(f"\nwrote {a.json_out}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSAL: {exc}", file=sys.stderr)
        sys.exit(2)
