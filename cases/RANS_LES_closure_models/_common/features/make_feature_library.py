#!/usr/bin/env python3
"""Render FEATURE_LIBRARY.md: every feature, its definition, invariance,
normaliser and source table/page. Generated from the manifest + measurements."""
from __future__ import annotations
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FEAT = "/home/ubuntu/closure-data/features"
man = json.load(open(os.path.join(FEAT, "manifest.json")))
iv = json.load(open(os.path.join(FEAT, "invariance_check.json")))
au = json.load(open(os.path.join(FEAT, "fs2_audit.json")))
names = man["features"]
ng = set(iv["not_galilean_invariant"]); nr = set(iv["not_rotation_invariant"])
dead = set(au["per_family"]["POOLED"]["dead_features"])

DESC = {
 "q1_wallRe": ("min(sqrt(k) d / (50 nu), 2)", "wall-distance Reynolds number",
               "none (already dimensionless)", "Wu Table 2 p. 9 / Kaandorp Table 1 p. 25"),
 "q2_turbIntensity": ("k / (k + 0.5 U.U)", "turbulence intensity", "0.5 U.U",
                      "Wu Table 2 p. 9 / Kaandorp Table 1 p. 25 (dagger)"),
 "q3_timeScaleRatio": ("(k/eps) / (k/eps + 1/||S||)", "turbulent : mean-strain time scale",
                       "1/||S||", "Wu Table 2 p. 9"),
 "q4_pgradAlongStreamline": ("U.grad p / (|U.grad p| + |U||grad p|)",
                             "pressure gradient along streamline", "|U||grad p|",
                             "Kaandorp Table 1 p. 25 (dagger)"),
 "q5_excessRotation": ("(||W||-||S||)/(||W||+||S||)", "excess rotation rate", "||W||+||S||",
                       "Kaandorp Table 1 p. 25"),
 "q6_stressRatio": ("||tau|| / (||tau|| + k)", "total : normal Reynolds stress", "k",
                    "Kaandorp Table 1 p. 25"),
 "q7_viscRatio": ("nu_t / (nu_t + 100 nu)", "eddy : molecular viscosity ratio", "100 nu",
                  "Kaandorp Table 1 p. 25"),
 "q8_kConvection": ("U.grad k / (|U.grad k| + |tau:S|)", "TKE convection : production",
                    "|tau_ij S_ij|", "Kaandorp Table 1 p. 25 (dagger)"),
 "q9_nonOrthogonality": ("|U_i U_j S_ij| / (. + |U|^2 ||S||)", "streamline non-orthogonality",
                         "|U|^2 ||S||", "Kaandorp Table 1 p. 25 (dagger)"),
 "q10_streamlineCurv": ("|U_i A_ij U_j| / (. + |U|^2 ||grad U||)", "streamline curvature marker",
                        "|U|^2 ||grad U||", "Kaandorp Table 1 p. 25 (dagger)"),
 "q11_turbReynolds": ("(sqrt(k)/(nu omega)) / (. + 50)", "turbulent Reynolds number", "50",
                      "Kaandorp Table 1 p. 25"),
}
for i, nm in enumerate(["lam1", "lam2", "lam3", "lam4", "lam5"], start=1):
    DESC[nm] = (f"tr of the {i}-th Pope invariant of (s, r)", "Pope integrity-basis invariant",
                "Durbin-bounded time scale T = max(k/eps, 6 sqrt(nu/eps))",
                "Pope 1975 JFM 72(2) p. 335")

L = []; A = L.append
A("# FS1 maximal feature library")
A("")
A("**Generated** by `make_feature_library.py`. Built by `build_features.py`; audited by")
A("`fs2_audit.py`; invariance measured by `invariance_check.py`. **Start maximal, select")
A("nothing** - no feature here has been chosen or discarded on any performance grounds.")
A("")
A(f"**{man['n_features']} features** on **{len(man['cases'])} benchmark cases** "
  f"({sum(m['n_cells'] for m in man['cases'].values()):,} cells). One `.npz` per case in")
A("`/home/ubuntu/closure-data/features/` (outside the repo), plus `manifest.json`.")
A("")
A("## Blocks")
A("")
A("| block | count | what | source |")
A("|---|---|---|---|")
A("| **A** | 47 | minimal integrity basis of `{S, Omega, A_p, A_k}`, normalisation **A** | Wu, Xiao & Paterson 2018, Table B.4, arXiv:1801.02762v4 preprint **p. 35**; mapping `A = -I x v` their Eq. (B.1a,b) **p. 35** |")
A("| **B** | 47 | the same 47 invariants, normalisation **B** | normalisation VARIANT, not new physics |")
A("| **C** | 11 | scalar flow markers `q1..q11` | Wu Table 2 **p. 9**; Kaandorp & Dwight 2020 Table 1 **p. 25** |")
A("| **D** | 5 | Pope's five invariants of `(s, r)` | Pope 1975, JFM 72(2), **p. 335** |")
A("")
A("## Normalisation, and the two variants")
A("")
A("Raw tensors are normalised by Wu et al.'s bounded scheme (their Eq. 8, **p. 9**), which")
A("keeps every normalised component in `[-1, 1]`:")
A("")
A("```")
A("alpha_hat = alpha / (|alpha| + |beta|)")
A("```")
A("")
A("with `beta` from their Table 1 (**p. 8**): `eps/k` for `S`, `||Omega||` for `Omega`,")
A("`rho |DU/Dt|` for `grad p`, `eps/sqrt(k)` for `grad k`.")
A("")
A("| variant | time scale used for `S` | carries `nu`? |")
A("|---|---|---|")
A("| **A** | `beta = eps/k`, i.e. `T = k/eps` | no |")
A("| **B** | `T = max(k/eps, 6 sqrt(nu/eps))` (Durbin bound) | **yes** |")
A("")
A("> **Reynolds-similarity note, required by lesson L-184/D2.** Variant **B** contains the")
A("> molecular viscosity through the Durbin bound. A normaliser carrying `nu` is **not**")
A("> Reynolds-similar: two geometrically identical flows at different `Re` do not map onto the")
A("> same normalised feature value. Variant B may therefore not be transferred across a")
A("> Reynolds-number change without an explicit note, and any model selecting B features must")
A("> report that it has done so. Variant A carries no `nu` and is Reynolds-similar. Both are")
A("> shipped precisely so the choice is visible and testable rather than buried.")
A("")
A("Block D also uses the Durbin-bounded scale and is **unbounded** - `|lam3|` reaches 1.5e11")
A("and `|lam5|` 1.5e14 on this data. That is recorded in `FS2_DEGENERACY_REPORT.md` sec. 5;")
A("it makes block D dominant in any unstandardised distance metric.")
A("")
A("## Wall distance: recomputed, and validated")
A("")
A("`q1_wallRe` needs a wall distance. The 29 parametric hills and the NASA hump ship")
A("`walldist`; the ducts, `PHLL10595` and `CBFS13700` do not. `wall_distance.py` recomputes it")
A("for every case as the nearest distance from each cell centre to any face centre on a patch")
A("of type `wall`, read from `constant/polyMesh`.")
A("")
A("**Validated against a shipped field** on `alpha_05_4071_2024` (a hill that ships `walldist`):")
A("**median relative difference 1.1e-14**, **p95 3.1e-3**, **relative L2 2.2e-3**. It is exact in")
A("the median and departs only in the near-wall cells where a face-centre distance is a lower")
A("bound on the true normal distance. `q1` saturates at 2, which bounds the consequence.")
A("")
A("## Invariance, measured not asserted")
A("")
A(f"Charter section 6 check on `{iv['case']}`: Galilean boost and rigid rotation applied to the")
A("raw fields, all features and normalisers recomputed. Tolerance `1e-12`.")
A("")
A(f"* **Rotation invariant: all {man['n_features']}** (max relative change "
  f"{iv['tests']['rotation']['max_rel_change']:.1e}, and the three above tolerance are "
  "roundoff on algebraically-zero features - see the report).")
A(f"* **NOT Galilean invariant: {len(ng)} of {man['n_features']}.** Every one either contains "
  "`A_p` (whose normaliser `|DU/Dt|` reduces to `|U.grad U|` in a steady solve, which shifts "
  "under a boost) or uses the raw velocity `U`.")
A("")
A("This independently reproduces Kaandorp & Dwight's own annotation: *\"Features marked with")
A("dagger are rotationally invariant but not Galilean invariant\"* (Table 1 footnote, **p. 25**).")
A("Their daggered features are `q2`, `q4`, `q8`, `q9`, `q10` - and those are exactly the five")
A("scalar markers this measurement flags.")
A("")
A("## Every feature")
A("")
A("`G` = Galilean invariant, `R` = rotation invariant, `dead` = algebraically zero on all")
A("pooled data (`max|v| < 1e-12`).")
A("")
A("| # | feature | definition | normaliser | G | R | dead | source |")
A("|---|---|---|---|---|---|---|---|")
for i, n in enumerate(names):
    base = n.split("__")[0]
    var = n.split("__")[1] if "__" in n else "-"
    if n in DESC:
        d, desc, norm, src = DESC[n]
        defn = f"{desc}: `{d}`"
    else:
        defn = f"`tr({base[2:]})`" if base.startswith("tr") else f"`{base}`"
        norm = f"variant **{var}**"
        src = "Wu Table B.4 p. 35"
    A(f"| {i+1} | `{n}` | {defn} | {norm} | {'no' if n in ng else 'yes'} | "
      f"{'no' if n in nr else 'yes'} | {'**DEAD**' if n in dead else ''} | {src} |")
A("")
A("## Reproducing")
A("")
A("```bash")
A("cd cases/RANS_LES_closure_models/_common/features")
A("/home/ubuntu/closure-venv/bin/python build_features.py     # -> /home/ubuntu/closure-data/features/*.npz")
A("/home/ubuntu/closure-venv/bin/python invariance_check.py   # -> invariance_check.json")
A("/home/ubuntu/closure-venv/bin/python fs2_audit.py          # -> fs2_audit.json")
A("/home/ubuntu/closure-venv/bin/python make_feature_library.py")
A("/home/ubuntu/closure-venv/bin/python make_fs2_report.py")
A("```")
A("")
open(os.path.join(HERE, "FEATURE_LIBRARY.md"), "w").write("\n".join(L) + "\n")
print(f"wrote FEATURE_LIBRARY.md ({len(L)+1} lines)")
