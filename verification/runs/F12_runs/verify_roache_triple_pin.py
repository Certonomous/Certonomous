#!/usr/bin/env python3
"""F12 -- THE `roache_triple` PIN, AS AN EXECUTABLE CHECK.

WHAT THIS IS.  `verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/
launch_f12_rung.py` records, in its own module docstring, a debt:

    "STILL OWED, and enforced by the interlock above rather than by a promise:
     `scripts/roache_triple.py` is NOT pinned.  That is correct for rung 1 -- a
     single rung cannot compute a triple -- and it is owed before rungs 2-5,
     where the triple IS the graded object."

This file DISCHARGES that debt.  It pins, by sha256 and by git blob, the
instrument that will grade F12's triple; it pins the exact arguments that
instrument must be called with; and it RE-DERIVES every band from the frozen
pre-registration's own thresholds rather than restating a number a reader would
have to trust.  It then proves, with controls, that the pinned bands actually
bind.

WHAT THIS IS NOT.  IT MOVES NO GATE.  Every threshold below is quoted from
`verification/campaign/F12_PREREGISTRATION.md` by line, and every band is
ARITHMETIC ON THAT THRESHOLD -- the same move the CAP-ENFORCEMENT ADDENDUM of
2026-08-25 made for the caps, whose own words are: "A conversion of a frozen
number into a different unit is not a new number."  F12 rung 1 has fired, so
VERIFICATION_CHARTER.md 2d is live and gates are CLOSED; nothing here alters a
gate, a threshold, a band, a cap or a label.  It does not authorise a launch, it
does not regrade rung 1 (`NOT A RESULT`) and it does not touch rung 2's
interlock (`BLOCKED`).

FAILS CLOSED.  Any sha drift, any band that does not re-derive, any control that
does not fire, and this exits non-zero having written nothing.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import os
import pathlib
import subprocess
import sys
import tempfile

REPO = pathlib.Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "sdk"))
sys.path.insert(0, str(REPO / "scripts"))

OUT = REPO / "verification/runs/F12_runs/roache_triple_pin.json"

# --- pinned bytes ----------------------------------------------------------
# The triple instrument.  Hashed WHOLE: it is the graded object's grader.
ROACHE_SHA256 = "452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051"
ROACHE_BLOB = "8dee0d31e94d3f59d28658f88a4cd6df80ae8e39"
# F12's frozen grading path, already pinned by the launcher at this same blob.
RAE_SHA256 = "d5db99d877f5389a7b2bfdb52c35822be0781bd7c65d31b573cc282b975c82ed"
RAE_BLOB = "a18314f77160b7a58f443073850a44b4d8fada7d"
# The frozen pre-registration, v1.4 (LAUNCHER ADDENDUM).
PREREG_BLOB = "462492a82b6cf848eaaff25661ded45e623e723f"
# Function-level pins: an unrelated edit elsewhere in a shared file must not
# silently change a graded function (the launcher's own discipline, adopted).
FN_SHA256 = {
    "shock_location":
        "59c75739ca9a1a12c85aac2d4e9436263326b8bbadf7b71e90f9ec6902a5263d",
    "cp_deviation":
        "6513b0f7142982765ba522d28e7d7958273e6018e6b11a9cd6596fdcfb3a10c0",
    "sonic_cp":
        "f395c50f680d40175c5eec0bbbc00f303b3d871d588d8fd6708c19ee076cc54f",
    "solver_converged":
        "aff97421a70be7af4ed134df408876d6cc47765398e27d5e9449b9f50b744bf8",
    "final_coefficient":
        "c5391c236e986ac3d23a8255120e13634498b06ad17e8e1ba158d069b2e6788b",
}

# --- the frozen thresholds, quoted by line ---------------------------------
# F12_PREREGISTRATION.md:60  "upper surface RMS <= 0.08"
GATE1_UPPER_MAX = 0.08
# F12_PREREGISTRATION.md:61  "lower surface RMS <= 0.04"
GATE1_LOWER_MAX = 0.04
# F12_PREREGISTRATION.md:69-72  "|x_shock(CFD) - x_shock(experiment)| <= 0.020"
GATE2_TOL = 0.020
# F12_PREREGISTRATION.md:86     "|CN - 0.803| / 0.803 <= 5%"
GATE3_REF, GATE3_FRAC = 0.803, 0.05
# F12_PREREGISTRATION.md:88     "|CD - 0.0168| / 0.0168 <= 20%"
GATE4_REF, GATE4_FRAC = 0.0168, 0.20
# F12_PREREGISTRATION.md:110-114  the three registered cell counts
CELLS = {"coarse": 23040, "medium": 92160, "fine": 368640}
# F12_PREREGISTRATION.md:18  workshop condition, the PRIMARY grade
MACH_WORKSHOP = 0.734
DIM = 2                      # 2D aerofoil.  require_dim() refuses a guess.

FAILURES: list[str] = []


def check(name, ok, detail=""):
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)
    return bool(ok)


def sha256_file(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def git_blob(rel):
    return subprocess.run(["git", "-C", str(REPO), "rev-parse", f"HEAD:{rel}"],
                          capture_output=True, text=True, check=True).stdout.strip()


def main():
    print("F12 roache_triple PIN -- executable verification")
    print("=" * 70)

    # (i) the instrument bytes -------------------------------------------------
    print("(i) instrument bytes, disk AND HEAD")
    rp = REPO / "scripts/roache_triple.py"
    check("roache_triple.py sha256 matches the pin",
          sha256_file(rp) == ROACHE_SHA256, sha256_file(rp)[:16])
    check("roache_triple.py disk == HEAD blob",
          git_blob("scripts/roache_triple.py") == ROACHE_BLOB, ROACHE_BLOB[:12])
    ra = REPO / "sdk/workflows/rae2822_case9.py"
    check("rae2822_case9.py sha256 matches the pin",
          sha256_file(ra) == RAE_SHA256, sha256_file(ra)[:16])
    check("rae2822_case9.py disk == HEAD blob (the launcher's pin)",
          git_blob("sdk/workflows/rae2822_case9.py") == RAE_BLOB, RAE_BLOB[:12])
    check("F12_PREREGISTRATION.md disk == HEAD blob",
          git_blob("verification/campaign/F12_PREREGISTRATION.md") == PREREG_BLOB,
          PREREG_BLOB[:12])
    if FAILURES:
        print("\nABORT: instrument bytes drifted; nothing further is meaningful.")
        return 2

    import roache_triple as RT                                    # noqa: E402
    from sdk.workflows import rae2822_case9 as W                  # noqa: E402

    print("(ii) function-level pins on the frozen grading path")
    for fn, want in FN_SHA256.items():
        got = hashlib.sha256(inspect.getsource(getattr(W, fn)).encode()).hexdigest()
        check(f"{fn}() source sha256", got == want, got[:16])

    # (iii) the module constants the pin depends on ---------------------------
    print("(iii) module constants")
    check("Fs == 1.25 (CLAUDE.md rule 5)", RT.FS == 1.25, str(RT.FS))
    check("planted-zero PLANT is non-zero", RT.PLANT != 0.0, str(RT.PLANT))

    # (iv) the ladder is EQUAL-ratio, and exactly so --------------------------
    print("(iv) refinement ratios re-derived from the registered cell counts")
    r21 = RT.refinement_ratio(CELLS["medium"], CELLS["fine"], DIM)
    r32 = RT.refinement_ratio(CELLS["coarse"], CELLS["medium"], DIM)
    check("r21 == 2 exactly", abs(r21 - 2.0) < 1e-12, f"{r21!r}")
    check("r32 == 2 exactly", abs(r32 - 2.0) < 1e-12, f"{r32!r}")
    check("the ladder is EQUAL-ratio, so form='equal' is REQUIRED",
          abs(r21 - r32) < 1e-12, f"gap {abs(r21 - r32):.3e}")

    # (v) the bands, RE-DERIVED from the frozen thresholds --------------------
    print("(v) bands re-derived from the frozen thresholds (no new numbers)")
    up = _read_taps(REPO / "verification/runs/F12_runs/reference/"
                           "rae2822_case9_cp_upper.dat")
    check("upper-surface reference taps read", len(up) == 52, f"n = {len(up)}")
    sl = W.shock_location(up, MACH_WORKSHOP)
    x_exp = sl["sonic_x_over_c"]
    check("Cp* re-derives from the frozen sonic_cp()",
          abs(sl["cp_star"] - W.sonic_cp(MACH_WORKSHOP)) == 0.0,
          f"Cp* = {sl['cp_star']!r}")
    check("x_shock(experiment) is a sonic crossing inside the window",
          x_exp is not None and 0.10 < x_exp < 0.95, f"x_exp = {x_exp!r}")
    check("the frozen tap spacing through the shock is ~0.025 c, as the "
          "pre-registration states at :82",
          abs(sl["steepest_resolution"] - 0.025) < 0.001,
          f"{sl['steepest_resolution']:.6f}")

    bands = {
        "gate1_cp_rms_upper": (0.0, GATE1_UPPER_MAX),
        "gate1_cp_rms_lower": (0.0, GATE1_LOWER_MAX),
        "gate2_x_shock_sonic": (x_exp - GATE2_TOL, x_exp + GATE2_TOL),
        "gate3_CN": (GATE3_REF * (1 - GATE3_FRAC), GATE3_REF * (1 + GATE3_FRAC)),
        "gate4_CD": (GATE4_REF * (1 - GATE4_FRAC), GATE4_REF * (1 + GATE4_FRAC)),
    }
    check("gate 3 band is the 5 % of :86, not a new number",
          abs(bands["gate3_CN"][0] - 0.76285) < 1e-12
          and abs(bands["gate3_CN"][1] - 0.84315) < 1e-12,
          f"{bands['gate3_CN']}")
    check("gate 4 band is the 20 % of :88, not a new number",
          abs(bands["gate4_CD"][0] - 0.01344) < 1e-12
          and abs(bands["gate4_CD"][1] - 0.02016) < 1e-12,
          f"{bands['gate4_CD']}")
    check("gate 2 band is +/- 0.020 c about the experimental sonic crossing",
          abs((bands["gate2_x_shock_sonic"][1]
               - bands["gate2_x_shock_sonic"][0]) - 2 * GATE2_TOL) < 1e-15,
          f"{bands['gate2_x_shock_sonic']}")

    # (vi) the controls: the bands must actually BIND ------------------------
    print("(vi) controls -- a band that cannot fail is not a band")
    check("CN at the reference PASSES its band",
          RT.band_verdict(GATE3_REF, bands["gate3_CN"])[0] == "PASS")
    check("CN 6 % high GATE FAILs (mutation control)",
          RT.band_verdict(GATE3_REF * 1.06, bands["gate3_CN"])[0] == "GATE FAIL")
    check("CN 6 % low GATE FAILs (mutation control, other side)",
          RT.band_verdict(GATE3_REF * 0.94, bands["gate3_CN"])[0] == "GATE FAIL")
    check("CD 21 % high GATE FAILs (mutation control)",
          RT.band_verdict(GATE4_REF * 1.21, bands["gate4_CD"])[0] == "GATE FAIL")
    check("an upper Cp RMS of 0.081 GATE FAILs (mutation control)",
          RT.band_verdict(0.081, bands["gate1_cp_rms_upper"])[0] == "GATE FAIL")
    check("x_shock 0.021 c downstream GATE FAILs (mutation control)",
          RT.band_verdict(x_exp + 0.021,
                          bands["gate2_x_shock_sonic"])[0] == "GATE FAIL")
    check("x_shock 0.019 c downstream PASSES (the band is not degenerate)",
          RT.band_verdict(x_exp + 0.019,
                          bands["gate2_x_shock_sonic"])[0] == "PASS")

    # (vii) planted-zero control on the read path (CLAUDE.md rule 3) ---------
    print("(vii) planted-zero control, on the read path a real grade uses")
    tmp = tempfile.mkdtemp(prefix="f12_pin_")
    series = os.path.join(tmp, "series.json")
    with open(series, "w") as fh:
        json.dump({"quantity": "control", "dim": DIM, "levels": [
            {"name": "coarse", "cells": CELLS["coarse"], "value": 1.16},
            {"name": "medium", "cells": CELLS["medium"], "value": 1.04},
            {"name": "fine", "cells": CELLS["fine"], "value": 1.01}]}, fh)
    pc = RT.planted_zero_control(series, "coarse")
    check("the reader SEES a planted perturbation", pc["passed"],
          f"planted {pc['planted']}, saw {pc['reader_delta']}")
    # NEGATIVE arm: a control that did not pass must REFUSE a grade.
    bad = dict(pc, passed=False)
    refused = False
    try:
        RT.grade_ladder("control", [
            {"name": "coarse", "cells": CELLS["coarse"], "value": 1.16},
            {"name": "medium", "cells": CELLS["medium"], "value": 1.04},
            {"name": "fine", "cells": CELLS["fine"], "value": 1.01}],
            DIM, (0.0, 2.0), bad,
            iterative_states={k: "CONVERGED" for k in CELLS})
    except (RT.Refusal, SystemExit):
        refused = True
    check("a FAILED planted-zero control REFUSES the grade", refused)

    # (viii) rule 5 step (a) on F12's own live states -------------------------
    print("(viii) rule 5 step (a) against F12's ACTUAL state today")
    row = RT.grade_ladder(
        "CN", [{"name": "coarse", "cells": CELLS["coarse"], "value": 0.803},
               {"name": "medium", "cells": CELLS["medium"], "value": 0.803},
               {"name": "fine", "cells": CELLS["fine"], "value": 0.803}],
        DIM, bands["gate3_CN"], pc,
        iterative_states={"coarse": "NOT CONVERGED",
                          "medium": "NOT RUN", "fine": "NOT RUN"})
    check("F12's live states force NOT A RESULT before any grid claim",
          row["verdict"] == "NOT A RESULT", row["why"][:70])
    check("the band verdict is still computed and printed beside it "
          "(the gate is one-way and that is checkable)",
          row["band_verdict"] == "PASS", row["band_verdict"])
    check("no GCI leaks onto a NOT A RESULT row", "GCI_pct" not in row)

    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}")
        return 1

    pin = {
        "what": "F12 roache_triple pin -- discharges the debt recorded in "
                "launch_f12_rung.py's docstring",
        "grades_nothing": True,
        "moves_no_gate": True,
        "prereg": {"path": "verification/campaign/F12_PREREGISTRATION.md",
                   "blob": PREREG_BLOB, "version": "1.4"},
        "instrument": {"path": "scripts/roache_triple.py",
                       "sha256": ROACHE_SHA256, "blob": ROACHE_BLOB,
                       "selftest": "53/53 checks passed"},
        "grading_path": {"path": "sdk/workflows/rae2822_case9.py",
                         "sha256": RAE_SHA256, "blob": RAE_BLOB,
                         "function_sha256": FN_SHA256},
        "call": {
            "entry": "roache_triple.grade_ladder",
            "dim": DIM,
            "fs": RT.FS,
            "form": "equal",
            "equal_tol": 0.0,
            "levels_coarse_first": [
                {"name": "coarse", "cells": CELLS["coarse"],
                 "run_dir": "attempt2_coarse_workshop_M0.734_a2.79"},
                {"name": "medium", "cells": CELLS["medium"],
                 "run_dir": "attempt2_medium_workshop_M0.734_a2.79"},
                {"name": "fine", "cells": CELLS["fine"],
                 "run_dir": "attempt2_fine_workshop_M0.734_a2.79"}],
            "r21": r21, "r32": r32,
            "representative_h": {k: RT.representative_h(v, DIM)
                                 for k, v in CELLS.items()},
            "iterative_states_source":
                "rae2822_case9.solver_converged() on each level's "
                "log.rhoSimpleFoam -- admission gate B, F12_PREREGISTRATION.md:54",
            "plateau_states": None,
            "plateau_states_note":
                "ABSENT, not passed. The frozen pre-registration carries no "
                "plateau clause, so none is invented here. grade_ladder's own "
                "docstring requires an absent measurement be recorded as absent "
                "and never as a pass (VERIFICATION_CHARTER.md section 9).",
            "plant_control_source":
                "roache_triple.external_plant_control(), planted into the "
                "OpenFOAM surface sample the case comparator actually reads, "
                "not into a synthetic series",
        },
        "bands_derived_from_frozen_thresholds": {
            "gate1_cp_rms_upper": {"band": list(bands["gate1_cp_rms_upper"]),
                                   "from": "F12_PREREGISTRATION.md:60 "
                                           "'upper surface RMS <= 0.08'"},
            "gate1_cp_rms_lower": {"band": list(bands["gate1_cp_rms_lower"]),
                                   "from": "F12_PREREGISTRATION.md:61 "
                                           "'lower surface RMS <= 0.04'"},
            "gate2_x_shock_sonic": {"band": list(bands["gate2_x_shock_sonic"]),
                                    "x_experiment": x_exp,
                                    "cp_star": sl["cp_star"],
                                    "steepest_resolution": sl["steepest_resolution"],
                                    "from": "F12_PREREGISTRATION.md:69-72, "
                                            "+/- 0.020 c about the experimental "
                                            "sonic crossing derived by the frozen "
                                            "shock_location() from "
                                            "reference/rae2822_case9_cp_upper.dat"},
            "gate3_CN": {"band": list(bands["gate3_CN"]),
                         "from": "F12_PREREGISTRATION.md:86 '|CN - 0.803|/0.803 "
                                 "<= 5%'"},
            "gate4_CD": {"band": list(bands["gate4_CD"]),
                         "from": "F12_PREREGISTRATION.md:88 '|CD - 0.0168|/0.0168 "
                                 "<= 20%'"},
        },
        "CM": {"band": None,
               "handling": "REPORTED, NOT GATED (F12_PREREGISTRATION.md:94-98). "
                           "grade_ladder REFUSES without a band, so CM must NOT "
                           "be passed to it. Its triple, state, observed order "
                           "and GCI are printed via all_triples() and no verdict "
                           "is emitted for it."},
        "rungs_4_and_5": {
            "triple": None,
            "why": "Rung 4 (medium, tape M = 0.730) and rung 5 (medium, 2x "
                   "far-field) are SINGLE-MESH sensitivity runs at one level "
                   "each. A Roache triple needs three levels of ONE experiment; "
                   "all_triples() refuses fewer than three. Neither rung owes a "
                   "triple and neither can carry one. They are reported as "
                   "sensitivities beside the graded ladder, never graded as a "
                   "grid family, and the frozen text's 'A single-mesh result is "
                   "not shipped' (:119) is what forbids promoting either.",
        },
        "verified_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                                       capture_output=True, text=True).stdout.strip(),
    }
    OUT.write_text(json.dumps(pin, indent=1) + "\n")
    print(f"\nALL CHECKS PASSED. pin written to {OUT}")
    return 0


def _read_taps(path):
    out = []
    for line in pathlib.Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        a = line.split()
        out.append((float(a[0]), float(a[1])))
    return out


if __name__ == "__main__":
    sys.exit(main())
