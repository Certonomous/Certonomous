#!/usr/bin/env python3
"""build_t10avf2.py -- T10a-VF2 clean-room case builder (STAGING DRAFT).

STATUS: DRAFT authored by a heat-transfer lane on the supervisor's staging
dispatch, 2026-09-07. NOT FROZEN, NOT PINNED. Per T10aVF2_PREREGISTRATION.md
(frozen c4d1e30a) sec.6 the builder is "cut at BUILD/launch ... diff-read and
pinned before the run" -- that diff-read is the SUPERVISOR's SUPERVISION_CHARTER
sec.3 check and is NOT performed by this lane. This file exists so the case
directories can be staged (age guard satisfied) and so the supervisor has a
concrete artifact to diff-read against the pre-registration and against the
FROZEN comparator analyse_t10avf2.py (git blob ebe19800..., DO NOT TOUCH).

WHAT IS REUSED VERBATIM (sec.6 "may reuse predecessor build_t10avf.py logic
verbatim"): every geometry/dict function -- sph_dict, ball_dict, shell_dict,
box_dict, cyl_dict, vf_dict, the controlDict/fvSchemes/fvSolution, geom_dict,
nfaces -- is IMPORTED from the frozen predecessor
verification/runs/T-family/T10aVF_runs/build_t10avf.py, not re-implemented here.
No solver is ever invoked and no 0/ (or any numeric time) directory is written:
the case holds only system/ and constant/ dictionaries. viewFactorsGen writes
constant/F at LAUNCH, not here.

WHAT IS ADDED HERE (the only new thing) is the CASE.json meta the FROZEN
comparator analyse_t10avf2.py reads and the predecessor CASE.json does not carry:
    role         in {graded, afix, gaussquad, inttol, report}
    twin         basename of the alpha=exp(-3/2) _afix twin (graded cases)
    N_control    control-patch (n_ev==0) face count, for the order guard
    family       order-guard grouping key
    gaussQuadTol echoed for role=gaussquad cases (VF-7')
The predecessor keys (alpha, GaussQuadTol, distTol, intTol, agglomeration,
nFacesExpected, geom, params, name) are preserved unchanged.

  >>> FLAG FOR THE SUPERVISOR'S sec.3 CHECK <<<
  The comparator's graded-case contract (a case with role in {None,graded} AND
  alpha==0.21 must (a) own a convex n_ev==0 CONTROL patch, (b) name an _afix
  twin that is ALSO analysed, (c) supply N_control and a family with >=2 levels)
  is satisfied cleanly ONLY by the concentric SPHERE family (S1_SPH_L1..L4 +
  their _afix twins: inner sphere = convex control, outer sphere = concave
  graded, 4 order-guard levels). It is NOT satisfied by the S2 single-body
  geometries as the predecessor case_list builds them: BOX/BALL/CYL have no
  convex internal control patch, and SHELL_c has no _afix twin. This draft
  therefore marks the SPHERE family role="graded" and marks every S2 geometry
  role="report" so the comparator EXCLUDES them from VF-4' Limb A (it grades
  role in {None,"graded"} only). Whether S2 geometries are meant to enter VF-4'
  Limb A -- and if so, with which added control patches / _afix twins -- is a
  DESIGN DECISION embedded in the frozen comparator's intent that the prereg
  text does not pin. The supervisor resolves it before the run; the comparator
  REFUSES (exit 2) on any mismatch, so a wrong mapping fails safe, never to a
  wrong verdict.
"""
import os, json, argparse, sys

_HERE = os.path.dirname(os.path.abspath(__file__))
# Import the FROZEN predecessor builder for its geometry/dict logic, verbatim.
_PRED = os.path.join(_HERE, "..", "T10aVF_runs")
sys.path.insert(0, os.path.abspath(_PRED))
import build_t10avf as P  # noqa: E402  (frozen predecessor; geometry/dicts reused verbatim)

A = 0.21
AE = P.ALPHA_EXACT  # exp(-3/2) = 0.22313016014842982


def n_control(geom, p):
    """Control-patch (convex, n_ev==0) face count for the order guard.
    SPH/SHELL: the INNER body is the convex control -> 6*N*N faces.
    Other geometries have no convex internal control patch here."""
    if geom in ("SPH", "SHELL"):
        return 6 * p["N"] * p["N"]
    return None


def case_list():
    """(name, geom, p, alpha, gauss, distTol, intTol, agglom, meta_extra).

    The (name, geom, p, alpha, gauss, distTol, intTol, agglom) columns are the
    predecessor's case_list VERBATIM; meta_extra is the only addition."""
    C = []
    # ---- S1: mesh family, concentric spheres (the VF-4' graded family) -------
    for tag, nr, N in [("L1", 4, 8), ("L2", 6, 12), ("L3", 8, 16), ("L4", 10, 20)]:
        base = f"S1_SPH_{tag}"
        C.append((base, "SPH", dict(nr=nr, N=N), A, 0.01, 8.0, 0.01, 0,
                  dict(role="graded", family="SPH", twin=f"{base}_afix",
                       N_control=6 * N * N)))
        C.append((f"{base}_afix", "SPH", dict(nr=nr, N=N), AE, 0.01, 8.0, 0.01, 0,
                  dict(role="afix", family="SPH", N_control=6 * N * N)))
    # ---- S2: geometry / convexity -- RUN for cost/coverage, role="report" ----
    #      (see the supervisor FLAG in the module docstring: these do NOT meet
    #       the frozen comparator's graded-case contract as built here.)
    for tag, N in [("c", 8), ("f", 16)]:
        C.append((f"S2_BOX_{tag}", "BOX", dict(N=N), A, 0.01, 8.0, 0.01, 0,
                  dict(role="report", family="BOX")))
        C.append((f"S2_SHELL_{tag}", "SHELL", dict(nr=max(3, N // 2), N=N), A,
                  0.01, 8.0, 0.01, 0, dict(role="report", family="SHELL")))
        C.append((f"S2_BALL_{tag}", "BALL", dict(nr=max(3, N // 2), N=N), A,
                  0.01, 8.0, 0.01, 0, dict(role="report", family="BALL")))
        C.append((f"S2_CYL_{tag}", "CYL", dict(N=N, Nz=N), A, 0.01, 8.0, 0.01, 0,
                  dict(role="report", family="CYL")))
    for g, N in [("BOX", 16), ("SHELL", 16), ("BALL", 16), ("CYL", 16)]:
        p = dict(N=N) if g == "BOX" else (dict(N=N, Nz=N) if g == "CYL"
                                          else dict(nr=N // 2, N=N))
        C.append((f"S2_{g}_f_afix", g, p, AE, 0.01, 8.0, 0.01, 0,
                  dict(role="report", family=g)))
    # ---- S3: generator knobs, fixed mesh (SPH L2) ----------------------------
    M = dict(nr=6, N=12)
    for a in [0.10, 0.15, 0.20, 0.22, 0.25, 0.30]:
        C.append((f"S3_alpha_{a:.3f}".replace(".", "p"), "SPH", M, a, 0.01, 8.0,
                  0.01, 0, dict(role="report", family="SPH_alpha")))
    # VF-7': the GaussQuadTol sweep. SPH L2 at 0.01 is S1_SPH_L2 (role graded);
    # the comparator's VF-7' selects role=="gaussquad" cases only, needs >=2
    # points and an 'outer' patch. The three GaussQuadTol points are all built
    # here with role="gaussquad" so VF-7' has a self-contained, non-overlapping
    # 3-point set {0.01, 0.001, 1e-6} on the SAME SPH L2 mesh.
    C.append(("S3_gauss_0p01", "SPH", M, A, 0.01, 8.0, 0.01, 0,
              dict(role="gaussquad", gaussQuadTol=0.01, family="SPH_gauss")))
    for g in [0.001, 1e-6]:
        C.append((f"S3_gauss_{g:g}".replace(".", "p").replace("-", "m"),
                  "SPH", M, A, g, 8.0, 0.01, 0,
                  dict(role="gaussquad", gaussQuadTol=g, family="SPH_gauss")))
    for d in [1.0, 4.0, 100.0]:
        C.append((f"S3_dist_{d:g}", "SPH", M, A, 0.01, d, 0.01, 0,
                  dict(role="report", family="SPH_dist")))
    # VF-11 (REPORTED ONLY): the intTol ray-shrink collapse case.
    C.append(("S3_intTol_1em4", "SPH", M, A, 0.01, 8.0, 1e-4, 0,
              dict(role="inttol", family="SPH_int")))
    C.append(("S3_agglom_10", "SPH", M, A, 0.01, 8.0, 0.01, 10,
              dict(role="report", family="SPH_agg")))
    C.append(("S3_agglom_10_afix", "SPH", M, AE, 0.01, 8.0, 0.01, 10,
              dict(role="report", family="SPH_agg")))
    return C


def build(root, name, geom, p, alpha, gauss, distTol, intTol, agglom, extra):
    """Call the FROZEN predecessor build() (writes system/ + constant/ dicts +
    CASE.json verbatim), then AUGMENT CASE.json with the comparator meta keys."""
    P.build(root, name, geom, p, alpha=alpha, gauss=gauss, distTol=distTol,
            intTol=intTol, agglom=agglom)
    cj = os.path.join(root, name, "CASE.json")
    meta = json.load(open(cj))
    for k, v in extra.items():
        meta[k] = v
    nc = n_control(geom, p)
    if nc is not None and "N_control" not in meta:
        meta["N_control"] = nc
    open(cj, "w").write(json.dumps(meta, indent=2) + "\n")
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.join(_HERE, "cases"))
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    C = case_list()
    if a.list:
        tot = 0
        for nm, g, p, al, gq, dt, it, ag, ex in C:
            n = P.nfaces(g, p)
            tot += n * n
            print("%-26s %-6s role=%-9s n=%5d alpha=%.6f gauss=%g"
                  % (nm, g, ex.get("role", "?"), n, al, gq))
        print("\n%d cases, sum n^2 = %.3e -> ~%.2f core-min at 2.84e-8/n^2"
              % (len(C), tot, 2.84e-8 * tot))
        return
    os.makedirs(a.root, exist_ok=True)
    for nm, g, p, al, gq, dt, it, ag, ex in C:
        m = build(a.root, nm, g, p, al, gq, dt, it, ag, ex)
        print("built %-26s role=%-9s n=%5d" % (nm, m.get("role"), m["nFacesExpected"]))


if __name__ == "__main__":
    main()
