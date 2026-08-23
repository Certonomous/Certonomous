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
               "none (already dimensionless)", "Wu Table 2 p. 10 / Kaandorp Table 1 p. 25"),
 "q2_turbIntensity": ("k / (k + 0.5 U.U)", "turbulence intensity", "0.5 U.U",
                      "Wu Table 2 p. 10 / Kaandorp Table 1 p. 25 (dagger)"),
 "q3_timeScaleRatio": ("(k/eps) / (k/eps + 1/||S||)", "turbulent : mean-strain time scale",
                       "1/||S||", "Wu Table 2 p. 10"),
 "q4_pgradAlongStreamline": ("U.grad p / (|U.grad p| + |U||grad p|)",
                             "pressure gradient along streamline", "|U||grad p|",
                             "Kaandorp Table 1 p. 25 (dagger)"),
 "q5_excessRotation": ("(||W||-||S||)/(||W||+||S||)", "excess rotation rate", "||W||+||S||",
                       "Kaandorp Table 1 p. 25"),
 "q6_stressRatio": ("||tau|| / (||tau|| + k)", "total : normal Reynolds stress", "k",
                    "Kaandorp Table 1 p. 25"),
 "q7_viscRatio": ("nu_t / (nu_t + 100 nu)", "eddy : molecular viscosity ratio", "100 nu",
                  "Ling & Templeton 2015 (NOT ON DISK - PENDING-MIT; no on-disk printed source; "
                  "absent from Kaandorp Table 1 p. 25, which was miscited here until 2026-08-23)"),
 "q8_kConvection": ("U.grad k / (|U.grad k| + |tau:S|)", "TKE convection : production",
                    "|tau_ij S_ij|", "Kaandorp Table 1 p. 25 (dagger)"),
 "q9_nonOrthogonality": ("|U_i U_j S_ij| / (. + |U|^2 ||S||)", "streamline non-orthogonality",
                         "|U|^2 ||S||", "Kaandorp Table 1 p. 25 (dagger)"),
 "q10_streamlineCurv": ("|U_i A_ij U_j| / (. + |U|^2 ||grad U||)", "streamline curvature marker",
                        "|U|^2 ||grad U||", "Wang, Wu & Xiao 2017 Table 1, arXiv:1606.07987v2 p. 10 "
                        "(NOT in Kaandorp Table 1 p. 25 - their nine scalars are Wang's ten minus curvature)"),
 "q11_turbReynolds": ("(sqrt(k)/(nu omega)) / (. + 50)", "turbulent Reynolds number", "50",
                      "Ling & Templeton 2015 (NOT ON DISK - PENDING-MIT; no on-disk printed source; "
                      "absent from Kaandorp Table 1 p. 25, which was miscited here until 2026-08-23)"),
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
A("| **A** | 47 | minimal integrity basis of `{S, Omega, A_p, A_k}`, normalisation **A** | Wu, Xiao & Paterson 2018, Table B.4, arXiv:1801.02762v4 preprint, caption **p. 36** (Appendix B opens p. 35); mapping `A = -I x v` their Eq. (B.1a,b) **p. 35** |")
A("| **B** | 47 | the same 47 invariants, normalisation **B** | normalisation VARIANT, not new physics |")
A("| **C** | 11 | scalar flow markers `q1..q11` | Wu Table 2 **p. 10** (q1-q3); Kaandorp & Dwight 2020 Table 1 **p. 25** (q4-q6, q8, q9); Wang, Wu & Xiao 2017 Table 1 **p. 10** (q10); q7/q11: Ling & Templeton 2015, **NOT ON DISK** (PENDING-MIT) |")
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
A("with `beta` from their Table 1 (**p. 9**): `eps/k` for `S`, `||Omega||` for `Omega`,")
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
A("Their table daggers **four** rows - `q2`, `q4`, `q8`, `q9` in this library's numbering")
A("(`q10` is not in their table; it is Wang, Wu & Xiao 2017's streamline curvature) - and the")
A("measurement here flags all four, plus `q10`, as the five raw-velocity scalar markers.")
A("(Dagger count read from a two-column pdftotext extraction of p. 25; a marker lost by the")
A("extractor would not be visible. Corrected from an earlier five-dagger claim, 2026-08-23;")
A("`CLOSURE_MODELLING_CHARTER.md` sec. 6 agrees on four.)")
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
        src = "Wu Table B.4 p. 36"
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
# Rule 6: dated amendments are appended to FEATURE_LIBRARY.md by hand and must
# survive regeneration -- this generator opens the file "w", so without the
# carry-forward below the very next run of the reproduce block printed above
# would silently delete them. Everything from the marker onward is preserved.
AMEND_MARK = "<!-- AMENDMENTS BELOW THIS MARKER ARE PRESERVED ACROSS REGENERATION (rule 6) -->"
DST = os.path.join(HERE, "FEATURE_LIBRARY.md")
carried = ""
if os.path.exists(DST):
    prev = open(DST).read()
    if AMEND_MARK in prev:
        carried = AMEND_MARK + prev.split(AMEND_MARK, 1)[1]
        assert carried.strip() != AMEND_MARK, "rule 6: amendment marker found but nothing after it"
open(DST, "w").write("\n".join(L) + "\n" + carried)
if carried:
    assert AMEND_MARK in open(DST).read(), "rule 6: amendments lost on write"
print(f"wrote FEATURE_LIBRARY.md ({len(L)+1} lines"
      f"{f' + {len(carried.splitlines())} carried amendment lines' if carried else ''})")
