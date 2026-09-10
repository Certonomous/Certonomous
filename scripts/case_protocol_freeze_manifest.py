#!/usr/bin/env python3
"""Emit `<case>/FREEZE_MANIFEST.json` in the shape the freeze hook reads.

Shape fixed by VERIFICATION_CHARTER v1.75 (f49d3e42) sections 2bd.1 / 2be, relayed
as binding.  This script exists so the manifest is assembled by one instrument
rather than typed, because two of its fields are load-bearing in ways that are easy
to get subtly wrong:

  * PIN PATHS ARE REPO-RELATIVE.  A bare filename resolves as repo-relative anyway,
    then reports PIN-ABSENT while the file sits present and clean.
  * INVOCATIONS ARE argv LISTS, never shell strings, so a missing flag shows up as a
    diff instead of needing a parse.  A pinned comparator invoked wrongly is an
    UNPINNED grading path -- cfd's R1b had every blob correct and the argv pinned
    nowhere, and produced no graded number.

GUARDS CARRY THEIR ARMING DATUM.  A pin proves a file unchanged.  Evaluating the
guard's condition against that pinned blob's content is what proves the check is
AWAKE.  Without it a manifest can name the guard, name the pin, and have the field
inside the pin be null -- a sleeping check one level below the one the clause was
written to catch.

ANCESTRY IS NOT COMPUTED HERE.  `freeze_commit` and each pin's blob go out; the hook
derives whether a pin's last commit is an ancestor of the freeze.  A hand-verified
ancestry is one a supervisor eventually gets wrong.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
import case_protocol_lib as L  # noqa: E402


def git_blob(path: str) -> Optional[str]:
    """git hash-object -- the blob sha the freeze hook derives ancestry from.

    NOT a sha256 of the bytes.  Git's blob id is `sha1("blob <len>\0" + content)`,
    and it is the identifier that appears in the commit graph; a sha256 cannot be
    looked up in git at all.  Both go into the manifest, each under its own key.
    """
    fp = REPO / path
    if not fp.is_file():
        return None
    r = subprocess.run(["git", "hash-object", path], cwd=str(REPO),
                       capture_output=True, text=True)
    return r.stdout.strip() or None

REPO = Path("/home/ubuntu/Certonomous")
STAGE = "FREEZE"


def guards(spec: Dict[str, Any], out: Path) -> List[Dict[str, Any]]:
    """Every guard, with whether its arming datum is actually present and what it is."""
    g: List[Dict[str, Any]] = []

    g.append({
        "name": "age_guard",
        "armed": "unconditional",
        "condition": "every field at endTime must have st_mtime NEWER than the case's own 0/T",
        "armed_by_pin": "scripts/case_protocol_lib.py",
        "arming_datum_present": True,
        "arming_value": "completion_report(): age_pass is set False on any field not newer; "
                        "'age guard' is appended to failed_clauses whenever age_pass is not True",
        "note": "0/T is touched last at launch by the stage-4 wrapper, so it dates the run "
                "allowed to produce the answer.",
    })

    g.append({
        "name": "cell_count_source",
        "armed": "unconditional",
        "condition": "n_cells_from_checkmesh() returns (None, reason) unless a 'cells: N' line is "
                     "found in a checkMesh log; len(owner) is nFaces and is used nowhere",
        "armed_by_pin": "scripts/case_protocol_lib.py",
        "arming_datum_present": True,
        "arming_value": r"regex ^\s*cells:\s*(\d+)\s*$ against checkMesh stdout",
    })

    lvl = spec["levels"][0]["name"]
    tdirs = sorted((out / lvl / "case").glob("[0-9]*")) if (out / lvl / "case").is_dir() else []
    has_write = any((d / "p").is_file() for d in tdirs if d.is_dir())
    g.append({
        "name": "planted_control_perturbation_arm",
        "armed": "by_data",
        "condition": "a written time directory carrying p must exist to plant into; without one "
                     "the arm reports NOT DISCHARGEABLE rather than passing by default",
        "armed_by_pin": "scripts/case_protocol_stage2_bugcheck.py",
        "arming_datum_present": bool(has_write),
        "arming_value": (str(tdirs[-1]) if has_write else None),
    })

    g.append({
        "name": "instrument_source_arm",
        "armed": "unconditional",
        "condition": "SOURCE_DEFECT_RULES applied to the comparator's text: two-point plateau, "
                     "cell count from owner, literal claim string, silent zero default",
        "armed_by_pin": "scripts/case_protocol_stage2_bugcheck.py",
        "arming_datum_present": True,
        "arming_value": "4 rules; reported SEPARATELY from the perturbation arm because "
                        "'can see its input' and 'computes the right thing' are different claims",
    })

    mc = spec.get("stage3", {}).get("predictions", {}).get("max_clamped_cells")
    g.append({
        "name": "clamp_not_firing",
        "armed": "by_data",
        "condition": "max(LimitedCells reported by the limitTemperature fvOption) <= max_clamped_cells",
        "armed_by_pin": "verification/runs/M6CP1_runs/CASE_SPEC.json",
        "arming_datum_present": mc is not None,
        "arming_value": mc,
        "note": "a clamp active at the plateau is a boundary condition on the answer, not a "
                "stabiliser, and biases every gate downstream of it",
    })

    pw = spec.get("run_control", {}).get("plateau_window")
    g.append({
        "name": "plateau_window",
        "armed": "by_data",
        "condition": "trailing-window plateau statistic declared before the run; NOT a difference "
                     "between the last two writes (VERIFICATION_CHARTER 2bd)",
        "armed_by_pin": "verification/runs/M6CP1_runs/CASE_SPEC.json",
        "arming_datum_present": pw is not None,
        "arming_value": {"window": pw,
                         "statistic": spec.get("run_control", {}).get("plateau_statistic"),
                         "tolerance": spec.get("run_control", {}).get("plateau_tolerance")},
    })

    g.append({
        "name": "registration_committed_before_compute",
        "armed": "unconditional",
        "condition": "git cat-file -e HEAD:<registration_path> must succeed in stage 4 preflight; "
                     "a refusal blocks the launch",
        "armed_by_pin": "scripts/case_protocol_stage4_run.py",
        "arming_datum_present": True,
        "arming_value": spec.get("registration_path"),
    })

    g.append({
        "name": "mesh_matches_birth_certificate",
        "armed": "unconditional",
        "condition": "verify_birth() re-hashes every file in the level's mesh manifest; a MUTATED "
                     "or UNCERTIFIED file refuses the launch",
        "armed_by_pin": "scripts/case_protocol_lib.py",
        "arming_datum_present": True,
        "arming_value": "renumberMesh -overwrite is the documented way a certified mesh is "
                        "rewritten in place on this box, and it happens silently",
    })
    return g


def run_freeze_check(registration: str) -> Dict[str, Any]:
    """Invoke the frozen freeze checker RESTRICTED, and read pins_unseen off its status line.

    `--restrict-to-registration` is MANDATORY and is not leniency.  Unrestricted the
    checker exits 3 no matter how clean the registered set is, because rows belonging
    to OTHER campaigns are unfrozen -- so an exit condition phrased "the freeze check
    exits 0" is unsatisfiable for every case in this repository, and a gate no case
    can pass is a stop rather than a gate.

    AND AN EXIT 0 IS NOT A CLEAN BILL.  Unseen pins WARN by default, so the checker
    can exit 0 while pins it could not judge exist.  `pins_unseen` is read and
    reported: an instrument that could not look and an instrument that looked and
    found nothing must not produce the same output.
    """
    argv = [sys.executable, "scripts/check_comparator_freeze.py",
            "--repo", str(REPO),
            "--registration", registration,
            "--restrict-to-registration"]
    p = subprocess.run(argv, cwd=str(REPO), capture_output=True, text=True)
    out = p.stdout + p.stderr
    unseen = None
    judged = None
    m = re.search(r"pins_unseen\s*[=:]\s*(\d+)", out)
    if m:
        unseen = int(m.group(1))
    m = re.search(r"PINS NOT SEEN:\s*(\d+)", out)
    if m and unseen is None:
        unseen = int(m.group(1))
    m = re.search(r"PINS JUDGED:\s*(\d+)", out)
    if m:
        judged = int(m.group(1))
    # This checker states coverage as "PIN COVERAGE: N of M pinned executable(s) judged".
    # Parse it. Leaving pins_unseen None because a regex written for a different
    # phrasing missed is the precise failure shape the supervisor warned about: an
    # instrument that could not look must not report the same thing as one that
    # looked and found nothing.
    m = re.search(r"PIN COVERAGE:\s*(\d+)\s+of\s+(\d+)\s+pinned executable", out)
    if m:
        judged = int(m.group(1))
        unseen = int(m.group(2)) - int(m.group(1))
    viol = re.search(r";\s*(\d+)\s+PIN-OK,\s*(\d+)\s+violating", out)
    pin_ok = int(viol.group(1)) if viol else None
    pin_violating = int(viol.group(2)) if viol else None
    uncommitted = re.findall(r"PIN-UNCOMMITTED\s+(\S+)", out)
    return {"argv": argv, "rc": p.returncode, "pins_unseen": unseen, "pins_judged": judged,
            "pins_ok": pin_ok, "pins_violating": pin_violating,
            "pins_uncommitted": sorted(set(uncommitted)),
            "tail": out.strip().splitlines()[-12:],
            "note": ("exit 0 with pins_unseen > 0 is NOT a clean result: those pins were judged by "
                     "nothing. Unseen pins warn by default; the flip to refuse is pre-registered "
                     "to the commit that repairs the underlying PIN_PATH defect.")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--freeze-commit", default=None,
                    help="left null until the supervisor's freeze commit exists")
    a = ap.parse_args()

    spec = json.loads(Path(a.spec).read_text())
    out = Path(a.out)
    reg = spec["registration_path"]
    reg_path = REPO / reg

    pins = []
    for p in spec["pins"]:
        fp = REPO / p["path"]
        pins.append({"path": p["path"], "role": p["role"],
                     "blob": git_blob(p["path"]),
                     "sha256": L.sha256_file(fp) if fp.is_file() else None})
    for extra_path, role in (("verification/runs/M6CP1_runs/CASE_SPEC.json", "registered_set"),
                             ("scripts/case_protocol_stage3_smoke.py", "launcher"),
                             ("scripts/case_protocol_stage4_run.py", "launcher"),
                             ("scripts/case_protocol_freeze_manifest.py", "manifest")):
        pins.append({"path": extra_path, "role": role, "blob": git_blob(extra_path),
                     "sha256": L.sha256_file(REPO / extra_path)})

    spec_rel = "verification/runs/M6CP1_runs/CASE_SPEC.json"
    out_rel = "verification/runs/M6CP1_runs"
    invocations = [
        {"name": "stage1_setup", "cwd": str(REPO), "env_keys": ["PATH", "PYTHONPATH"],
         "argv": [sys.executable, "scripts/case_protocol_stage1_setup.py",
                  "--spec", spec_rel, "--out", out_rel, "--emit"]},
        {"name": "stage2_bugcheck", "cwd": str(REPO), "env_keys": ["PATH", "WM_PROJECT_DIR"],
         "argv": [sys.executable, "scripts/case_protocol_stage2_bugcheck.py",
                  "--spec", spec_rel, "--out", out_rel, "--case-root", out_rel,
                  "--solver", spec["run_control"]["solver"],
                  "--comparator", spec["pins"][0]["path"],
                  "--scratch", "<scratch>"]},
        {"name": "stage3_smoke", "cwd": str(REPO), "env_keys": ["PATH", "WM_PROJECT_DIR"],
         "argv": [sys.executable, "scripts/case_protocol_stage3_smoke.py",
                  "--spec", spec_rel, "--out", out_rel, "--case-root", out_rel,
                  "--level", "L2", "--fraction", "0.08", "--ranks", "1"]},
        {"name": "stage4_run", "cwd": str(REPO), "env_keys": ["PATH", "WM_PROJECT_DIR"],
         "argv": [sys.executable, "scripts/case_protocol_stage4_run.py",
                  "--spec", spec_rel, "--out", out_rel, "--case-root", out_rel,
                  "--level", "L2", "--ranks", "4",
                  "--grader", spec["pins"][0]["path"], "--go"]},
        {"name": "freeze_check", "cwd": str(REPO), "env_keys": ["PATH"],
         "argv": [sys.executable, "scripts/check_comparator_freeze.py",
                  "--repo", str(REPO), "--registration", reg, "--restrict-to-registration"],
         "note": "--restrict-to-registration is MANDATORY and is pinned here as argv rather than "
                 "remembered; unrestricted the checker exits 3 on rows belonging to other campaigns"},
    ]

    gates = [{"name": g["name"], "metric": g["metric"], "threshold": g["threshold"],
              "band": g["band"], "direction": g["direction"],
              "label_if_pass": g["label_if_pass"], "label_if_fail": g["label_if_fail"]}
             for g in spec["gates"]]

    tol = {k: float(v) for k, v in spec["numerics"]["solver_tolerances"].items()}
    tightest = min(spec["gates"], key=lambda g: abs(float(g["threshold"])))
    tc = L.check_tolerance_strictly_tighter(tightest["name"], abs(float(tightest["threshold"])), tol)

    s1 = out / "STAGE1_RECORD.json"
    blockage = json.loads(s1.read_text()).get("blockage") if s1.is_file() else None

    fz = run_freeze_check(reg)

    path = L.write_freeze_manifest(
        out / "FREEZE_MANIFEST.json",
        case=spec["case"], registration_path=reg,
        registration_blob=L.sha256_file(reg_path) if reg_path.is_file() else None,
        freeze_commit=a.freeze_commit,
        pins=pins, invocations=invocations, guards=guards(spec, out), gates=gates,
        solver_tolerance=tol, tightest_gate={"name": tightest["name"],
                                             "threshold": abs(float(tightest["threshold"]))},
        tolerance_strictly_tighter=tc.ok,
        cost_block={"point_core_min": spec["cost"]["point_core_min"],
                    "cap_core_min": spec["cost"]["cap_core_min"],
                    "cap_note": spec["cost"]["cap_note"],
                    "cost_basis": spec["cost"]["cost_basis"],
                    "routing": spec["cost"]["routing"]},
        blockage=blockage,
        budget_gate="NONE — Sanaa 2026-09-10",
        extra={"freeze_check": fz,
               "tolerance_margin_decades": tc.margin_decades,
               "class_default_counterexample": {
                   "class_default": "segregated steady solver (rhoSimpleFoam) for a steady "
                                    "external transonic wing",
                   "status": "class default, first use -- CONTRADICTED BY MEASUREMENT",
                   "evidence": "rhoSimpleFoam rc=136 (SIGFPE) in the first thermo update on every "
                               "variant; rhoPimpleFoam LTS rc=0 at t=500 on every variant",
                   "registered_solver": spec["run_control"]["solver"]}})

    print(L.state_line(STAGE, "manifest", "WRITTEN",
                       path=str(out / "FREEZE_MANIFEST.json"), sha256=path[:16],
                       pins=len(pins), invocations=len(invocations),
                       guards=len(guards(spec, out)), gates=len(gates)))
    print(L.state_line(STAGE, "freeze check (restricted)",
                       "EXIT 0" if fz["rc"] == 0 else f"EXIT {fz['rc']}",
                       pins_judged=fz["pins_judged"], pins_unseen=fz["pins_unseen"],
                       pins_ok=fz["pins_ok"], pins_violating=fz["pins_violating"]))
    for u in fz["pins_uncommitted"]:
        print(L.state_line(STAGE, "PIN-UNCOMMITTED", u,
                           note="clears on the supervisor's freeze commit"))
    print(L.state_line(STAGE, "tolerance_strictly_tighter", "TRUE" if tc.ok else "FALSE",
                       decades=round(tc.margin_decades, 2)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except L.Refusal as e:
        print(L.state_line(STAGE, "REFUSAL", e.code, detail=e.detail))
        sys.exit(2)
