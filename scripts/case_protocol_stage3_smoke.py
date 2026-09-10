#!/usr/bin/env python3
"""THE CASE PROTOCOL -- STAGE 3: SMOKE.

EXIT CONDITION
    A run of 5 to 10 percent of the registered full length, on the COARSEST level,
    matches predictions that were registered and hashed BEFORE it started.

FAILURE ACTION -- FIXED, NOT DISCRETIONARY
    Fail  -> take ONE registered ladder change, the next unspent rung, and re-smoke.
    Two fails attributed to the SAME CAUSE -> climb a rung: mesh, then numerics,
        then model, in that order.  The order is not a preference: a numerics change
        that compensates for a mesh defect hides the defect, and a model change that
        compensates for either is how a wrong answer becomes a tuned one.
    Three fails -> PARK the case NOT A RESULT and write the lesson.  Parking is the
        designed outcome of an exhausted ladder, not an admission of defeat.

WHY PREDICTIONS COME FIRST
    A smoke read after the fact will always look reasonable, because the reader
    knows the answer.  The predictions are written, hashed, and the hash printed
    BEFORE the solver is started, so the comparison afterwards is against a document
    that provably could not have been chosen to fit.

WHAT A PASS HERE IS AND IS NOT
    A smoke that reaches its end time with rc = 0 proves the solver SURVIVES.  It
    proves nothing about the answer.  A pseudo-transient run that survives is the
    beginning of the case and not the end of it.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_protocol_lib as L  # noqa: E402

STAGE = "STAGE3"

RUNG_ORDER = ["mesh", "numerics", "model"]


def write_predictions(out: Path, spec: Dict[str, Any], level: str, frac: float) -> Tuple[Path, str]:
    """Register the predictions and hash them BEFORE any solver starts."""
    rc = spec["run_control"]
    steps = int(round(frac * float(rc["end_time"])))
    pr = spec["stage3"]["predictions"]
    doc = {
        "case": spec["case"], "stage": 3, "level": level,
        "registered_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "smoke_fraction_of_full_run": frac,
        "smoke_steps": steps,
        "full_run_steps": rc["end_time"],
        "predictions": pr,
        "decision_rule": (
            "EVERY prediction must hold. A smoke that satisfies some predictions and not others "
            "is a FAIL, not a partial pass -- the predictions were chosen because each of them "
            "independently distinguishes a run that is working from one that is not."),
        "what_a_pass_means": (
            "the solver survives this configuration for this many steps and its state is within "
            "the registered envelope. It does NOT mean the answer is right, and no gate is "
            "graded here."),
    }
    p = out / f"STAGE3_PREDICTIONS_{level}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2) + "\n")
    return p, L.sha256_file(p)


def read_series(log: Path) -> Dict[str, List[float]]:
    """Residual and bound series out of a solver log, per field."""
    txt = log.read_text(errors="replace") if log.is_file() else ""
    out: Dict[str, List[float]] = {}
    for m in re.finditer(r"Solving for (\w+), Initial residual = ([0-9.eE+\-]+)", txt):
        out.setdefault(m.group(1), []).append(float(m.group(2)))
    out["_ExecutionTime"] = [float(m.group(1)) for m in
                             re.finditer(r"^ExecutionTime = ([0-9.eE+\-]+)", txt, re.M)]
    out["_Tmax"] = [float(m.group(1)) for m in
                    re.finditer(r"UnlimitedTmax=([0-9.eE+\-]+)", txt)]
    out["_clampedCells"] = [float(m.group(1)) for m in
                            re.finditer(r"Type=Upper,\s*LimitedCells=(\d+)", txt)]
    return out


def evaluate(pred: Dict[str, Any], series: Dict[str, List[float]], rc: int,
             log: Path) -> List[Dict[str, Any]]:
    """Check each registered prediction.  Every one is reported, pass or fail."""
    res: List[Dict[str, Any]] = []

    def add(name: str, ok: Optional[bool], got: Any, want: Any, detail: str = "") -> None:
        res.append({"prediction": name, "pass": ok, "measured": got, "registered": want,
                    "detail": detail})

    add("rc_zero", rc == 0, rc, 0,
        "rc read from the solver process, not from a wrapper")

    ex = series.get("_ExecutionTime", [])
    add("completed_steps_at_least", len(ex) >= pred["min_steps"], len(ex), pred["min_steps"],
        "ExecutionTime lines are completed iterations; Time lines include the one it died in")

    for fld, cap in pred["max_final_residual"].items():
        s = series.get(fld, [])
        add(f"final_residual_{fld}", (bool(s) and s[-1] <= cap), (s[-1] if s else None), cap)

    for fld in pred["must_not_grow"]:
        s = series.get(fld, [])
        if len(s) < 20:
            add(f"no_growth_{fld}", None, len(s), ">=20 samples",
                "too few samples to judge growth; NOT counted as a pass")
            continue
        head = sum(s[:10]) / 10.0
        tail = sum(s[-10:]) / 10.0
        add(f"no_growth_{fld}", tail <= head * pred["growth_factor_max"],
            tail / head if head else None, pred["growth_factor_max"],
            "mean of the last 10 samples over the mean of the first 10")

    tmax = series.get("_Tmax", [])
    add("T_below_ceiling", (bool(tmax) and max(tmax) <= pred["max_T_K"]),
        (max(tmax) if tmax else None), pred["max_T_K"],
        "UnlimitedTmax is the temperature BEFORE the clamp; it is the honest one")

    ex = series.get("_ExecutionTime", [])
    if len(ex) >= 2:
        per_it = (ex[-1] - ex[0]) / (len(ex) - 1)
        add("cost_per_iteration_s", per_it <= pred["max_cost_per_iteration_s"],
            round(per_it, 3), pred["max_cost_per_iteration_s"],
            "CASE_PROTOCOL_CHARTER section 3: cost per iteration within the estimate's band")
    else:
        add("cost_per_iteration_s", None, len(ex), ">=2 ExecutionTime lines", "too few samples")

    cl = [float(m.group(1)) for m in
          re.finditer(r"^\s*Cl:\s*([0-9.eE+\-]+)", log.read_text(errors="replace"), re.M)] \
        if log.is_file() else []
    g = pred["graded_quantity_sign_and_order"]
    lo, hi = g["band"]
    add("graded_quantity_sign_and_order", (bool(cl) and lo <= cl[-1] <= hi),
        (cl[-1] if cl else None), g["band"],
        "the previous attempt on this mesh reported Cl = -0.308 and Cd = 1.52 with rc = 0; "
        "rc = 0 did not catch it and a sign-and-order prediction does")

    clamped = series.get("_clampedCells", [])
    add("clamp_not_firing", (not clamped) or max(clamped) <= pred["max_clamped_cells"],
        (max(clamped) if clamped else 0), pred["max_clamped_cells"],
        ("a clamp that is ACTIVE is a boundary condition on the answer, not a stabiliser. "
         "If it fires here it will bias every gate downstream and the run is not gradeable."))
    return res


def next_rung(history: List[Dict[str, Any]], ladder: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Pick the next ladder change, honouring the two-fails-same-cause rule.

    The rule exists because the natural move after a failure is to try a variation
    of the thing that just failed, and two variations of the same idea are one
    attempt spent twice.
    """
    spent = {h["rung_id"] for h in history}
    causes = [h.get("cause") for h in history]
    tier = 0
    if len(causes) >= 2 and causes[-1] is not None and causes[-1] == causes[-2]:
        last_tier = max((RUNG_ORDER.index(h["tier"]) for h in history if h.get("tier") in RUNG_ORDER),
                        default=-1)
        tier = min(last_tier + 1, len(RUNG_ORDER) - 1)
    for want in RUNG_ORDER[tier:]:
        for r in ladder:
            if r["tier"] == want and r["id"] not in spent:
                return r
    return None


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--case-root", required=True)
    ap.add_argument("--level", required=True, help="the COARSEST admitted level")
    ap.add_argument("--fraction", type=float, default=0.08, help="5 to 10 percent of the full run")
    ap.add_argument("--ranks", type=int, default=1)
    ap.add_argument("--register-only", action="store_true",
                    help="write and hash the predictions and STOP, without running anything")
    a = ap.parse_args(argv)

    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out)
    if not (0.05 <= a.fraction <= 0.10):
        print(L.state_line(STAGE, "fraction", "REFUSED",
                           got=a.fraction, allowed="0.05 to 0.10"))
        return 2

    pred_path, pred_sha = write_predictions(out, spec, a.level, a.fraction)
    print(L.state_line(STAGE, "predictions registered", "FROZEN",
                       path=str(pred_path), sha256=pred_sha[:16]))
    if a.register_only:
        print(L.state_line(STAGE, "EXIT", "PENDING",
                           reason="predictions registered; smoke not run on this invocation"))
        return 0

    src = Path(a.case_root) / a.level / "case"
    smoke = out / a.level / "smoke"
    if smoke.exists():
        shutil.rmtree(smoke)
    smoke.mkdir(parents=True, exist_ok=True)
    for rel in ("system", "0"):
        shutil.copytree(src / rel, smoke / rel)
    (smoke / "constant").mkdir(exist_ok=True)
    for f in (src / "constant").iterdir():
        if f.name == "polyMesh":
            (smoke / "constant" / "polyMesh").symlink_to(f.resolve())
        else:
            shutil.copy2(f, smoke / "constant" / f.name)

    steps = int(round(a.fraction * float(spec["run_control"]["end_time"])))
    cd = smoke / "system" / "controlDict"
    cd.write_text(re.sub(r"^endTime\s+\S+;", f"endTime         {steps};",
                         cd.read_text(), flags=re.M))

    # 0/T is touched LAST, so it dates the run allowed to produce this answer (rule 4).
    os.utime(smoke / "0" / "T", None)

    solver = spec["run_control"]["solver"]
    log = smoke / f"log.{solver}"
    t0 = time.time()
    with open(log, "w") as fh:
        p = subprocess.Popen(L.foam_cmd([solver, "-case", str(smoke)], smoke),
                             stdout=fh, stderr=subprocess.STDOUT)
        rc = p.wait()
    wall = time.time() - t0
    (smoke / "RC.txt").write_text(f"RC={rc}\n")

    series = read_series(log)
    checks = evaluate(spec["stage3"]["predictions"], series, rc, log)
    c = L.cost(wall, a.ranks, f"stage-3 smoke, {steps} steps at level {a.level}")

    for ch in checks:
        print(L.state_line(STAGE, f"prediction {ch['prediction']}",
                           "PASS" if ch["pass"] else ("NOT EVALUABLE" if ch["pass"] is None else "FAIL"),
                           measured=ch["measured"], registered=ch["registered"]))
    print(L.state_line(STAGE, "cost", "MEASURED", core_min=round(c.core_min, 3),
                       usd_derived=round(c.usd_derived, 4), wall_s=round(wall, 1), ranks=a.ranks))

    failed = [ch for ch in checks if ch["pass"] is not True]
    verdict = "PASS" if not failed else "FAIL"
    hist_path = out / "STAGE3_LADDER_HISTORY.json"
    history = json.loads(hist_path.read_text()) if hist_path.is_file() else []

    action: Optional[Dict[str, Any]] = None
    if failed:
        cause = failed[0]["prediction"]
        history.append({"attempt": len(history) + 1, "rung_id": spec["stage3"].get("current_rung", "baseline"),
                        "tier": spec["stage3"].get("current_tier", "baseline"),
                        "cause": cause, "failed": [f["prediction"] for f in failed],
                        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        if len(history) >= 3:
            print(L.state_line(STAGE, "ladder", "EXHAUSTED", attempts=len(history)))
            print(L.state_line(STAGE, "EXIT", "NOT A RESULT",
                               reason="three smoke failures; case parked with its lesson"))
            hist_path.write_text(json.dumps(history, indent=2) + "\n")
            return 6
        action = next_rung(history, spec["stage3"]["ladder"])
        print(L.state_line(STAGE, "next ladder change",
                           action["id"] if action else "NONE LEFT",
                           tier=(action or {}).get("tier"),
                           change=(action or {}).get("change")))
        hist_path.write_text(json.dumps(history, indent=2) + "\n")

    record = {"stage": 3, "case": spec["case"], "level": a.level, "fraction": a.fraction,
              "steps": steps, "rc": rc, "rc_source": "Popen.wait()", "verdict": verdict,
              "predictions_path": str(pred_path), "predictions_sha256": pred_sha,
              "checks": checks, "cost": c.as_dict(), "next_action": action,
              "history": history}
    (out / f"STAGE3_RECORD_{a.level}.json").write_text(json.dumps(record, indent=2) + "\n")

    if verdict == "PASS":
        print(L.state_line(STAGE, "EXIT", "PASS",
                           note="stage 4 may be launched; a surviving smoke is not a graded result"))
        return 0
    print(L.state_line(STAGE, "EXIT", "FAIL", attempt=len(history)))
    return 5


if __name__ == "__main__":
    try:
        sys.exit(main())
    except L.Refusal as e:
        print(L.state_line(STAGE, "REFUSAL", e.code, detail=e.detail))
        sys.exit(2)
