#!/usr/bin/env python3
"""B-52 turn closure: 2 more draws at rung 6 (-> n=5), 1 at rung 7 (-> n=3).

Pre-registration: campaign/B52_TURN_CLOSURE_PREREGISTRATION.md, commit
f4ccfe92, committed before any new mesh existed. Reuses the gates and the
mesh/solve machinery of run_rung6_replicates.py (G1 cell admission, G2 birth
certificate, G3 settle, lever echo) -- see that module.

The verdict is read off the 90% CI on T, never the point estimate
(pre-registration section 4).
"""
from __future__ import annotations
import json, math, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_rung6_replicates as r6
from chief_engineer import mesh_certificate
from scipy.stats import chi2

RUNS = r6.RUNS
TURN = 4.055e-3

RUNG = {
    "rung6": {"cells": 330950,
              "existing": {"finer2": "study-b52-finer2-uq",
                           "rung6b": "study-b52-rung6b-uq",
                           "rung6c": "study-b52-rung6c-uq"},
              "new": {"rung6d": [(50,45,77),(53,45,73),(49,45,78)],
                      "rung6e": [(53,45,73),(49,45,78),(54,45,72)]}},
    "rung7": {"cells": 441057,
              "existing": {"rung7": "study-b52-rung7-uq",
                           "rung7b": "study-b52-rung7b-uq"},
              "new": {"rung7c": [(54,49,84),(57,48,82),(55,48,84)]}},
}
TEMPLATES = {"rung6": "study-b52-rung8-uq", "rung7": "study-b52-rung8-uq"}


def g1(cells: int, ref: int) -> bool:
    return abs((cells - ref) / ref) <= r6.CELL_TOL


def build_and_solve(name: str, candidates, ref_cells: int, template: str) -> dict:
    attempts = []
    case = RUNS / f"study-b52-{name}-uq"
    # L-42 guard: never re-stage over a case that already holds an admitted mesh.
    cert = mesh_certificate.read_certificate(case / "constant") if case.exists() else None
    if cert is not None and g1(cert.get("cells", 0), ref_cells):
        r6.log(f"{name}: case already holds an admitted certified mesh "
               f"({cert['cells']} cells); not re-staging (L-42)")
        info = {"mesh_wall_s": None, "certificate": cert}
        attempts.append({"divisions": None, "cells": cert["cells"],
                         "admitted": True, "note": "carried from an earlier invocation"})
    else:
        info = None
        for divisions in candidates[:r6.MAX_ATTEMPTS]:
            r6.TEMPLATE = RUNS / template
            remote = r6.stage(name, divisions)
            got = r6.mesh(remote, name)
            cells = got["certificate"]["cells"]
            ok = g1(cells, ref_cells)
            attempts.append({"divisions": list(divisions), "cells": cells,
                             "deviation": (cells - ref_cells) / ref_cells,
                             "admitted": ok,
                             "max_skewness": got["certificate"]["max_skewness"],
                             "certificate_verdict": got["certificate"]["verdict"]})
            r6.log(f"{name}: attempt {len(attempts)} {divisions} -> {cells} cells, "
                   f"{(cells-ref_cells)/ref_cells:+.2%} vs {ref_cells}, "
                   f"{'ADMITTED' if ok else 'RE-DRAW'}")
            if ok:
                info = got
                break
        if info is None:
            raise RuntimeError(f"{name}: re-draw allowance exhausted")
    out = {"draw_attempts": attempts, "certificate": info["certificate"],
           "mesh_wall_s": info["mesh_wall_s"], "case": str(case)}
    out.update(r6.solve(case, name))
    out["settle"] = r6.settle(case, name)
    for f, dst in (("log.checkMesh", f"{name}.log.checkMesh"),
                   ("constant/birth_certificate.json", f"{name}.birth_certificate.json")):
        src = case / f
        if src.exists():
            shutil.copy2(src, r6.HERE / dst)
    return out


def sd(vals):
    n = len(vals); m = sum(vals)/n
    return math.sqrt(sum((v-m)**2 for v in vals)/(n-1))


def main() -> int:
    r6.log("B52 turn closure arm starting (prereg f4ccfe92)")
    cd = {}
    results = {}
    for rung, spec in RUNG.items():
        cd[rung] = {}
        for tag, dirname in spec["existing"].items():
            cd[rung][tag] = r6.settle(RUNS / dirname, f"{tag} (existing)")["cd"]
        for name, cands in spec["new"].items():
            rec = build_and_solve(name, cands, spec["cells"], TEMPLATES[rung])
            results[name] = rec
            cd[rung][name] = rec["settle"]["cd"]

    s6 = sd(list(cd["rung6"].values())); n6 = len(cd["rung6"])
    s7 = sd(list(cd["rung7"].values())); n7 = len(cd["rung7"])
    var = s6**2 + s7**2
    T = TURN / math.sqrt(var)
    nu = var**2 / (s6**4/(n6-1) + s7**4/(n7-1))
    T_lo = T / math.sqrt(nu/chi2.ppf(0.05, nu))
    T_hi = T / math.sqrt(nu/chi2.ppf(0.95, nu))
    if T_lo >= 3.0:
        branch, reading = "SIGNAL", ("the turn is real structure; the withdrawn "
            "shape claims are reinstated, with a band")
    elif T_hi <= 1.0:
        branch, reading = "NOISE", ("the turn is indistinguishable from a "
            "draw-to-draw difference; the Tier-1 withdrawals become permanent")
    elif T_lo > 1.0 and T_hi < 3.0:
        branch, reading = "MARGINAL", ("a verdict, not a shrug: the turn is "
            "genuinely between noise and signal and established as such. No "
            "amount of further drawing makes it a signal, so the shape claims "
            "stay withdrawn/amended permanently and the matter closes")
    else:
        branch, reading = "INDETERMINATE", ("precision failure, not a physical "
            "finding: the 90% CI straddles a threshold. No branch is claimed. "
            "This was pre-registered (P1) as the expected outcome")
    out = {"prereg": "campaign/B52_TURN_CLOSURE_PREREGISTRATION.md",
           "prereg_commit": "f4ccfe92", "timestamp": r6.now(),
           "cd_by_rung": cd, "n6": n6, "n7": n7, "s6": s6, "s7": s7,
           "turn": -TURN, "T_hat": T, "welch_nu": nu,
           "T_ci90": [T_lo, T_hi], "branch": branch, "reading": reading,
           "P2_s6_in_bracket": 1.2e-3 <= s6 <= 3.2e-3,
           "P3_sigmas_differ_by_more_than_2x": (max(s6,s7)/min(s6,s7)) > 2.0,
           "s7_over_s6": s7/s6,
           "new_draws": results}
    (r6.HERE / "closure_record.json").write_text(
        json.dumps(out, indent=2, sort_keys=True, default=str) + "\n")
    r6.log(f"s6={s6:.4e} (n={n6})  s7={s7:.4e} (n={n7})  T={T:.3f}  nu={nu:.2f}  "
           f"CI90=[{T_lo:.3f}, {T_hi:.3f}]  -> {branch}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
