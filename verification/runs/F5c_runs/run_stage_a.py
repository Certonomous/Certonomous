#!/usr/bin/env python3
"""F5c retargeted arm -- STAGE A: regenerate the -10.5% with provable levers.

Pre-registration: campaign/F5C_UNSTEADY_PROBE_PREREGISTRATION.md, commit
3734270d (pre-launch correction d64565c1). Chief approval 2026-08-10: STAGE A
ALONE (15.5 core-min); Stage B is NOT approved and is not run here.

The three legs, exactly as filed in section 5:
  A1  coarse, SIMPLEC (consistent yes, relax p 0.3 / U 0.6), 2,000 it, sample 50
  A2  coarse, SIMPLEC,                                       8,000 it, sample 200
  A3  coarse, plain SIMPLE (consistent no, relax p 0.15 / U 0.4), 2,000 it, s 50

Bars scored here (section 4):
  M1  REGENERATED if |x_r/H - 5.6| <= 0.81 (one `coarse` face spacing at the
      crossing -- the best this detector can do). A2 is the leg that scores it.
  M2  PROVEN if A1 and A3 echo DIFFERENT sha256 for system/fvSolution AND
      |dx_r/H| > 0.81. Chief binding: the hash difference is the whole point,
      because this is the first time the algorithm attribution becomes provable.

Chief policy, binding on this run: NO WANDER VERDICT (M3) MAY BE CLAIMED FROM
ANY `coarse` RUN -- the wall faces near the crossing are 0.55-0.81 H apart
against a 0.20 H bar. The x_r history is recorded and reported as a number; it
is not scored, and Stage B (never run, not approved) is where M3 lives.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO / "sdk"))
from workflows.backstep_case import STEP_LEVELS, run_case  # noqa: E402
from chief_engineer import lever_echo  # noqa: E402

HERE = REPO / "demo-output" / "website" / "campaign" / "F5c_runs"
SCRATCH = Path("/home/ubuntu/certonomous-runs")
DRIVER_LOG = HERE / "stage_a_driver.log"

X_R_CORRECTED_HEADLINE = 5.6      # the number being regenerated
X_R_REFERENCE = 6.26              # Driver & Seegmiller
COARSE_FACE_SPACING = 0.81        # H, worst spacing near the crossing on coarse

LEGS = (
    {"name": "A1", "level": "coarse", "iterations": 2000, "sample_every": 50,
     "consistent": True, "relax_p": 0.3, "relax_u": 0.6,
     "basis_s": 142.6, "basis": "F5bc evidence table row 3, identical config"},
    {"name": "A2", "level": "coarse", "iterations": 8000, "sample_every": 200,
     "consistent": True, "relax_p": 0.3, "relax_u": 0.6,
     "basis_s": 672.4, "basis": "F5bc evidence table row 4, identical config"},
    {"name": "A3", "level": "coarse", "iterations": 2000, "sample_every": 50,
     "consistent": False, "relax_p": 0.15, "relax_u": 0.4,
     "basis_s": 115.3, "basis": "F5bc evidence table row 1, identical config"},
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(msg: str) -> None:
    line = f"[{now()}] {msg}"
    print(line, flush=True)
    HERE.mkdir(parents=True, exist_ok=True)
    with DRIVER_LOG.open("a") as handle:
        handle.write(line + "\n")


def fvsolution_hash(record: dict) -> str | None:
    for entry in (record.get("levers_verified_active") or {}).get("verified", []):
        if entry["file"] == "system/fvSolution":
            return entry["sha256"]
    return None


def run_leg(leg: dict) -> dict:
    level = next(l for l in STEP_LEVELS if l.name == leg["level"])
    out_dir = SCRATCH / f"f5c-stageA-{leg['name']}"
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    log(f"{leg['name']}: {leg['level']} {level.cells} cells, "
        f"{'SIMPLEC' if leg['consistent'] else 'SIMPLE'} "
        f"relax p{leg['relax_p']}/U{leg['relax_u']}, {leg['iterations']} it "
        f"(basis {leg['basis_s']}s = {leg['basis_s']/60:.2f} core-min)")
    start = time.monotonic()
    record = run_case(level, out_dir, iterations=leg["iterations"],
                      sample_every=leg["sample_every"],
                      consistent=leg["consistent"], relax_p=leg["relax_p"],
                      relax_u=leg["relax_u"], timeout=7200, log=log)
    wall = time.monotonic() - start
    record["leg"] = leg["name"]
    record["wall_s"] = round(wall, 1)
    record["core_min"] = round(wall / 60.0, 3)
    record["basis_core_min"] = round(leg["basis_s"] / 60.0, 3)
    record["basis"] = leg["basis"]
    record["fvSolution_sha256"] = fvsolution_hash(record)
    log(f"{leg['name']}: x_r/H = {record.get('x_r_over_h')} "
        f"(nearwall check {record.get('x_r_over_h_nearwall_U')}), "
        f"{record['core_min']:.2f} core-min vs basis "
        f"{record['basis_core_min']:.2f}, "
        f"fvSolution sha256 {str(record['fvSolution_sha256'])[:12]}, "
        f"cert {(record.get('mesh_certificate') or {}).get('verdict')}")

    # Archive: postProcessing is gitignored, so the artifacts the claims rest
    # on are lifted out with the existing collector or they do not survive --
    # which is exactly how the original six runs were lost.
    dest = HERE / f"stage_a_{leg['name']}"
    shutil.rmtree(dest, ignore_errors=True)
    result = subprocess.run(
        [sys.executable, str(HERE / "collect.py"), str(out_dir), str(dest)],
        capture_output=True, text=True)
    if result.returncode != 0:
        log(f"{leg['name']}: collect.py rc={result.returncode} "
            f"{result.stderr.strip()[:300]}")
    else:
        log(f"{leg['name']}: archived to {dest.name}")
    for extra in ("log.checkMesh", "constant/birth_certificate.json"):
        src = out_dir / "case" / extra
        if src.exists():
            dst = dest / Path(extra).name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (dest / "record.json").write_text(
        json.dumps({k: v for k, v in record.items()
                    if k not in ("wall_shear_profile", "pressure_profile")},
                   indent=2, sort_keys=True, default=str) + "\n")
    return record


def score(records: dict[str, dict]) -> dict:
    a1, a2, a3 = records["A1"], records["A2"], records["A3"]

    # M1 -- scored on A2, the 8,000-iteration SIMPLEC leg.
    out: dict = {}
    xr2 = a2.get("x_r_over_h")
    if xr2 is None:
        out["M1"] = {"branch": "NO_CROSSING",
                     "reading": "A2's detector found no reattachment crossing "
                                "at all; the -10.5% headline is not "
                                "regenerated and retracts to unmeasured"}
    else:
        delta = abs(xr2 - X_R_CORRECTED_HEADLINE)
        out["M1"] = {
            "x_r_over_h": xr2, "target": X_R_CORRECTED_HEADLINE,
            "delta": delta, "bar": COARSE_FACE_SPACING,
            "branch": "REGENERATED" if delta <= COARSE_FACE_SPACING
                      else "NOT_REGENERATED",
            "deviation_vs_reference_pct":
                100.0 * (xr2 - X_R_REFERENCE) / X_R_REFERENCE,
            "reading": ("the -10.5% headline is on evidence rails: archived "
                        "case, retained log, hash-bound levers"
                        if delta <= COARSE_FACE_SPACING else
                        "the headline does NOT come back from the "
                        "configuration it is attributed to; it retracts to "
                        "unmeasured and F5c's status reverts to open")}

    # M2 -- A1 vs A3: the hash MUST differ (chief binding), and the answers
    # must differ by more than the detector can blur.
    h1, h3 = a1.get("fvSolution_sha256"), a3.get("fvSolution_sha256")
    x1, x3 = a1.get("x_r_over_h"), a3.get("x_r_over_h")
    hashes_differ = bool(h1) and bool(h3) and h1 != h3
    dx = abs(x1 - x3) if (x1 is not None and x3 is not None) else None
    if not hashes_differ:
        branch, reading = "VOID", (
            "the two legs echoed the SAME fvSolution sha256 (or none): the "
            "SIMPLE/SIMPLEC lever did not actually differ between the runs, "
            "so nothing about the algorithm is provable from this pair")
    elif dx is None:
        branch, reading = "UNRESOLVED", (
            "hashes differ as required, but one leg produced no crossing, so "
            "the algorithm's effect on x_r cannot be read")
    elif dx > COARSE_FACE_SPACING:
        branch, reading = "PROVEN", (
            "for the first time the algorithm attribution is log-provable: "
            "different fvSolution bytes ran, bound by sha256, and the answers "
            "differ by more than this detector can blur")
    else:
        branch, reading = "NOT_RESOLVABLE", (
            "different fvSolution bytes provably ran, but the x_r difference "
            "is inside the coarse detector's own face spacing -- the honest "
            "reading is that the algorithm choice is not resolvable here, NOT "
            "that it does nothing")
    out["M2"] = {"fvSolution_sha256_A1": h1, "fvSolution_sha256_A3": h3,
                 "hashes_differ": hashes_differ, "x_r_A1": x1, "x_r_A3": x3,
                 "delta_x_r": dx, "bar": COARSE_FACE_SPACING,
                 "branch": branch, "reading": reading}

    # M3 -- recorded, NOT scored. Chief policy.
    histories = {}
    for name, rec in records.items():
        hist = [(t, v) for t, v in (rec.get("x_r_over_h_history") or [])
                if v is not None]
        half = hist[len(hist) // 2:]
        vals = [v for _, v in half]
        histories[name] = {
            "samples": len(hist), "second_half_samples": len(vals),
            "second_half_peak_to_peak": (max(vals) - min(vals)) if vals else None,
            "second_half_min": min(vals) if vals else None,
            "second_half_max": max(vals) if vals else None,
            "first": hist[0] if hist else None, "last": hist[-1] if hist else None}
    out["M3_recorded_not_scored"] = {
        "policy": ("Chief policy for this case, 2026-08-10: no wander verdict "
                   "may be claimed from any `coarse` run. Wall faces near the "
                   "crossing are 0.55-0.81 H apart against a 0.20 H "
                   "materiality bar, so this detector cannot support one in "
                   "either direction. M3 belongs to Stage B, which is not "
                   "approved and was not run."),
        "histories": histories}
    return out


def main() -> int:
    HERE.mkdir(parents=True, exist_ok=True)
    log("F5c STAGE A starting -- prereg 3734270d (correction d64565c1), "
        "chief-approved Stage A only, 15.5 core-min")
    records: dict[str, dict] = {}
    for leg in LEGS:
        records[leg["name"]] = run_leg(leg)
    scored = score(records)
    total = sum(r["core_min"] for r in records.values())
    basis = sum(r["basis_core_min"] for r in records.values())
    out = {
        "arm": "F5c Stage A -- regenerate -10.5% with provable levers",
        "prereg": "campaign/F5C_UNSTEADY_PROBE_PREREGISTRATION.md",
        "prereg_commit": "3734270d (correction d64565c1)",
        "chief_approval": "Stage A alone, 15.5 core-min; Stage B NOT approved",
        "timestamp": now(),
        "scored": scored,
        "legs": {n: {k: v for k, v in r.items()
                     if k not in ("wall_shear_profile", "pressure_profile",
                                  "x_r_over_h_history")}
                 for n, r in records.items()},
        "cost_core_min": {"measured": round(total, 3),
                          "pre_registered_basis": round(basis, 3),
                          "ratio": round(total / basis, 3) if basis else None},
    }
    (HERE / "stage_a_record.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    log(f"M1 {scored['M1']['branch']} | M2 {scored['M2']['branch']} | "
        f"{total:.2f} core-min vs {basis:.2f} pre-registered")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
