#!/usr/bin/env python3
r"""Curriculum D19O -- the comparator's controls.

THE FIXTURES ARE WRITTEN BY THE REAL PRODUCERS.  Every FD row comes from
`d19o_xf.build_fd_row`, every control row from `d19o_xf.build_ctrl_row`, every
ledger row from `d19o_run_arm.sh`'s OWN `d19o_ledger_row` function, sourced and
called.  On 2026-08-31 SO-1c refused because its consumer read `gates` at the top
level while its producer wrote them at `grade.gates`, and a 51-leg suite could
not see it BECAUSE ITS FIXTURES WERE HAND-BUILT FROM THE CONSUMER'S OWN
EXPECTATIONS.  If the launcher's row format and the comparator's regex ever
diverge here, the fixture rows stop parsing and this suite fails LOUDLY.

A GREEN SUITE IS NOT A RESULT ABOUT THE RUN.  It is a result about the
comparator.  No arm of D19O has run; nothing here is validated against a real
D19O artefact, and that residual is R1 in PREREGISTRATION.md section 15.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import d19o_xf as XF                                              # noqa: E402
import d19o_age_guard as AGE                                      # noqa: E402
import d19o_grade as G                                            # noqa: E402

FAILED = []


def unit(name, want, got, note=""):
    good = (got == want)
    if not good:
        FAILED.append(name)
    print("  %-22s expect=%-24s got=%-24s %s%s"
          % (name, str(want)[:24], str(got)[:24],
             "OK" if good else "**FAILED**", (" " + note) if note else ""))
    return good


# ---- D19R's REAL measured numbers, re-read at this freeze --------------------
ADJ_CD = {("shape", 0): -0.007221766503489129, ("shape", 3): 0.0092905364130168,
          ("shape", 6): -0.014133812719678937, ("shape", 7): -0.00020994801762558475,
          ("patchV", 1): 0.001959450045064941}
ADJ_CL = {("shape", 0): 1.0735917332902383, ("shape", 3): 1.368550326026575,
          ("shape", 6): -0.255135617198591, ("shape", 7): 0.4888695416188753,
          ("patchV", 1): 0.09990780123049972}
CD0, CL0 = 0.014600274357917864, 0.42288451566070906


def _pair(dcd, dcl, step, cd0=CD0, cl0=CL0):
    return (cd0 + dcd * step, cd0 - dcd * step, cl0 + dcl * step, cl0 - dcl * step)


def _ledger_row_via_launcher(**kw):
    """THE LAUNCHER'S OWN FUNCTION, sourced and called.  Not a Python copy."""
    args = [kw["arm"], kw["row"], kw["img"], kw["digest"], str(kw["rc"]),
            str(kw["wall_s"]), str(kw["ranks"]), str(kw["core_min"]), str(kw["cap"]),
            str(kw["enforced_wall_s"]), str(kw["enforced_core_min"]), kw["mem"],
            kw["inspect"], kw["pre"], kw["post"], kw["cpuset"], kw["delivered"],
            kw["sib_pre"], kw["sib_post"], kw["log"], kw["stamp"]]
    r = subprocess.run(
        ["bash", "-c", '. "%s" --source-only; d19o_ledger_row "$@"'
         % os.path.join(HERE, "d19o_run_arm.sh"), "_"] + args,
        capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise SystemExit("the launcher's own ledger writer did not run: rc=%d %s"
                         % (r.returncode, r.stderr[:400]))
    return r.stdout.strip()


def build_root(tmp, *, converged=True, majors=12, reduction=6.0,
               shape7_perfect=False, arms=None, cpuset=None, ranks=None,
               so_md5=None, core_min=None, drop_evals=0, baseline_designpoint=False,
               plant_opt_in_endpoint=False, malform=None):
    """A COMPLETE run root, written by the real writers."""
    arms = arms or list(G.ARMS_DECLARED)
    root = os.path.join(tmp, "CURRICULUM-D19O-a1-naca0012-subsonic-optimisation")
    os.makedirs(root, exist_ok=True)

    ledger = ["ITEM=D19O"]
    for arm in arms:
        d = os.path.join(root, arm)
        os.makedirs(d, exist_ok=True)
        row = G.ARM_ROW[arm]
        kind = G.ARM_KIND[arm]
        rk = (ranks or {}).get(arm, G.ARM_RANKS[arm])
        cm = (core_min or {}).get(arm, G.PREDICTED_CORE_MIN[arm])
        cs = (cpuset or {}).get(arm, G.CPUSET_REGISTERED)
        so = (so_md5 or {}).get(arm, G.SO_MD5[row])
        stamp = "20260901T000000Z_%d" % (1000 + arms.index(arm))
        log = "%s_%s.log" % (arm, stamp)
        ledger.append(_ledger_row_via_launcher(
            arm=arm, row=row, img="img:%s" % row.lower(), digest=G.DIGEST[row], rc=0,
            wall_s=int(cm * 60 / rk), ranks=rk, core_min=cm, cap=G.CAPS[arm],
            enforced_wall_s=int(G.CAPS[arm] * 60 / rk) - 180,
            enforced_core_min="%.6f" % G.CAPS[arm], mem="12g", inspect="0 false",
            pre="27.00", post="27.00", cpuset=cs, delivered="0.9900 n=5",
            sib_pre="", sib_post="", log=log, stamp=stamp))
        ledger.append("D19O_G9_OK arm=%s libidwarp_so_md5=%s digest=%s"
                      % (arm, so, G.DIGEST[row]))

        # ---- the arm's own log, carrying its terminal statement --------------
        term = ("D19O_MESH_IDENTITY_ALL_OK" if kind == "SCRIPT" else G.TERMINAL[kind])
        with open(os.path.join(root, log), "w") as fh:
            fh.write("D4S_IDWARP_SO_MD5: %s\n" % so)
            fh.write("SIMPLE: no convergence criteria found\n")   # benign, counted
            fh.write("trapFpe: Floating point exception trapping enabled\n")
            fh.write("time step continuity errors : sum local = 1e-12\n")
            fh.write("Minimal residual 9.1e-09 satisfied the prescribed tolerance\n")
            fh.write("%s\n" % term)

        # ---- the age-guard inputs, then the sentinel, then the artefact ------
        for sub in ("0.orig", "system"):
            os.makedirs(os.path.join(d, sub), exist_ok=True)
        for f in ("U", "T", "p"):
            with open(os.path.join(d, "0.orig", f), "w") as fh:
                fh.write("internalField uniform 0;\n")
        with open(os.path.join(d, "system", "decomposeParDict"), "w") as fh:
            fh.write("numberOfSubdomains 1;\n")
        spath, datum = AGE.stamp_sentinel(root, arm, [root])
        manifest = AGE.build_manifest(d, ["0.orig", "system"])
        with open(os.path.join(d, ".d19o_manifest.json"), "w") as fh:
            json.dump(manifest, fh, indent=1, sort_keys=True)

        time.sleep(0.01)
        xopt_shape = ["0.0"] * 8 if baseline_designpoint else \
            ["0.001", "0.002", "-0.001", "0.003", "0.004", "-0.002", "0.001", "0.0005"]
        xopt_patchv = ["100.0", "5.2"]

        if kind == "SCRIPT":
            with open(os.path.join(d, "checkMesh.log"), "w") as fh:
                fh.write("    cells:            %d\n" % G.MESH_CELLS)
        elif kind == "O":
            cd_f = CD0 * (1.0 - reduction / 100.0)
            with open(os.path.join(d, "opt_IPOPT.txt"), "w") as fh:
                fh.write("iter objective inf_pr inf_du lg(mu) ||d|| lg(rg) alpha_du alpha_pr ls\n")
                for i in range(majors):
                    fh.write(" %3d  1.0e-02 1.00e-06 %8.2e  -5.0 1.00e-03  -1.0 1.00e+00 "
                             "1.00e+00  1\n" % (i, 10.0 ** (-i - 1)))
                if converged:
                    fh.write("\nEXIT: Optimal Solution Found.\n")
                    fh.write("Number of Iterations....: %d\n" % (majors - 1))
                else:
                    fh.write("\nEXIT: Maximum Number of Iterations Exceeded.\n")
            L = G.STALL.read_log(os.path.join(d, "opt_IPOPT.txt"))
            doc = {"item": "D19O", "mode": "O", "row": row, "nprocs": rk,
                   "producer_md5": XF.PRODUCER_MD5,
                   "CD_baseline_trimmed": repr(CD0), "CL_baseline_trimmed": repr(CL0),
                   "CD_final": repr(cd_f), "CL_final": repr(0.5),
                   "CL_target": 0.5, "drag_reduction_pct": repr(reduction),
                   "ipopt_exit": L["convergence"]["exit"],
                   "ipopt_n_iterations": L["convergence"]["n_iterations"],
                   "ipopt_printed_convergence": L["convergence"]["converged"],
                   "ipopt_table_rows": L["n_rows"], "stall": L["stall"],
                   "dv_final": {"shape": xopt_shape, "patchV": xopt_patchv},
                   "excluded_from_aggregate": [[d0, i0] for d0, i0 in
                                               XF.EXCLUDED_FROM_AGGREGATE]}
            with open(os.path.join(d, "d19o_O.json"), "w") as fh:
                json.dump(doc, fh, indent=1, sort_keys=True)
            with open(os.path.join(d, XF.XOPT), "w") as fh:
                json.dump({"item": "D19O", "row": row, "shape": xopt_shape,
                           "patchV": xopt_patchv, "CD_final": repr(cd_f),
                           "CL_final": repr(0.5)}, fh, indent=1, sort_keys=True)
        elif kind == "XE":
            adjs = {"CD": {"shape": [repr(ADJ_CD.get(("shape", i), 0.0)) for i in range(8)],
                           "patchV": [repr(0.000285), repr(ADJ_CD[("patchV", 1)])]},
                    "CL": {"shape": [repr(ADJ_CL.get(("shape", i), 0.0)) for i in range(8)],
                           "patchV": [repr(0.00885), repr(ADJ_CL[("patchV", 1)])]}}
            with open(os.path.join(d, "d19o_X.json"), "w") as fh:
                json.dump({"item": "D19O", "mode": "XE", "row": row, "adjoint": adjs,
                           "at_design_point": XF.XOPT, "no_optimiser_ran": True,
                           "design_point": {"shape": xopt_shape, "patchV": xopt_patchv},
                           "excluded_from_aggregate": [[a, b] for a, b in
                                                       XF.EXCLUDED_FROM_AGGREGATE]},
                          fh, indent=1, sort_keys=True)
        else:                                                     # FE
            rows_out, declared = [], 2
            for dv, idx in XF.COMPONENTS:
                per = {}
                for s in list(XF.FD_STEPS_ENDPOINT[dv]) + [XF.TB_STEP]:
                    declared += 2
                    a_cd, a_cl = ADJ_CD[(dv, idx)], ADJ_CL[(dv, idx)]
                    if s == XF.TB_STEP:
                        # the trivial baseline MUST be noise: 40x off
                        per[s] = _pair(a_cd * 40.0, a_cl * 40.0, s)
                    elif (dv, idx) == ("shape", 7) and not shape7_perfect:
                        # D19R's REAL shape[7] curve: flat at 1e-2/1e-3, broken at 1e-4
                        real = {1.0e-2: -2.089091733992e-04, 1.0e-3: -2.064883285469e-04,
                                1.0e-4: -1.630004736741e-04}
                        per[s] = _pair(real[s], a_cl, s)
                    else:
                        per[s] = _pair(a_cd * 1.0002, a_cl * 1.0002, s)
                rows_out.append(XF.build_fd_row(dv, idx, per))     # THE REAL WRITER
            rows_out.append(XF.build_ctrl_row(CD0, CL0))           # THE REAL WRITER
            with open(os.path.join(d, "d19o_F.json"), "w") as fh:
                json.dump({"item": "D19O", "mode": "FE", "row": row,
                           "at_design_point": XF.XOPT, "no_optimiser_ran": True,
                           "design_point": {"shape": xopt_shape, "patchV": xopt_patchv},
                           "rows": rows_out, "n_rows": len(rows_out),
                           "evaluations_declared": declared - drop_evals,
                           "evaluations_failed": 0, "evaluation_failures": [],
                           "contains_adjoint": False,
                           "excluded_from_aggregate": [[a, b] for a, b in
                                                       XF.EXCLUDED_FROM_AGGREGATE]},
                          fh, indent=1, sort_keys=True)
            if plant_opt_in_endpoint:
                open(os.path.join(d, "opt_IPOPT.txt"), "w").write("planted\n")
            if malform == arm:
                open(os.path.join(d, "d19o_F.json"), "w").write("{not json")

    with open(os.path.join(root, "ledger.txt"), "w") as fh:
        fh.write("\n".join(ledger) + "\n")
    return root


def _grade(root):
    try:
        return G.grade(root), None
    except G.Refusal as exc:
        return None, json.loads(str(exc))["REFUSE"]


def main():
    print("D19O COMPARATOR SELFTEST")
    print("  d19o_grade.py md5 : %s" % G.md5_of(os.path.join(HERE, "d19o_grade.py")))
    print()
    tmp = tempfile.mkdtemp(prefix="d19o_grade_")
    try:
        # ============ A. THE CEILING -- THE LOAD-BEARING CONTROL ==============
        print("A. THE VERDICT CEILING -- THIS ITEM CANNOT PUBLISH PASS")
        r = build_root(os.path.join(tmp, "a"))
        g, ref = _grade(r)
        unit("A0-no-refusal", None, ref)
        print("     rows: SHIPPED=%s PATCHED=%s ; item raw=%s -> final=%s"
              % (g["rows"]["SHIPPED"]["verdict"], g["rows"]["PATCHED"]["verdict"],
                 g["verdict_before_ceiling"], g["verdict"]))
        # THE CEILING BINDS AT ROW LEVEL AND THE ITEM INHERITS.  So the ITEM's
        # own `verdict_before_ceiling` is already GATE REACHED (it composed from
        # two capped rows), and `capped_by_ceiling` at item level is False.  That
        # is correct and it is also the shape of a true field that could leave a
        # false impression, so the record carries `capped_by_ceiling_anywhere`.
        unit("A1-item-raw", "GATE REACHED", g["verdict_before_ceiling"],
             "(the item composes from ALREADY-CAPPED rows -- see A5)")
        unit("A2-final-capped", "GATE REACHED", g["verdict"])
        unit("A3-capped-anywhere", True, g["capped_by_ceiling_anywhere"],
             "(the ceiling DID bind, at row level, and the item record says so)")
        unit("A3b-rows-named", ["PATCHED", "SHIPPED"],
             sorted(g["rows_capped_by_ceiling"]))
        unit("A4-rows-capped", ["GATE REACHED"] * 2,
             [g["rows"][x]["verdict"] for x in ("SHIPPED", "PATCHED")])
        unit("A5-row-raw-PASS", ["PASS"] * 2,
             [g["rows"][x]["verdict_before_ceiling"] for x in ("SHIPPED", "PATCHED")])
        unit("A6-in-vocab", True, g["verdict"] in G.VOCAB)
        unit("A7-ceiling-only-worsens", "NOT A RESULT", G._apply_ceiling("NOT A RESULT")[0],
             "(the ceiling NEVER improves a verdict)")
        unit("A8-gate-fail-through", "GATE FAIL", G._apply_ceiling("GATE FAIL")[0])
        unit("A9-prov-satisfied", "SATISFIED", g["gates"]["G-PROV"]["verdict"])
        unit("A10-prov-links", 2, g["gates"]["G-PROV"]["n_links"])

        # ============ B. shape[7] IS NOT RESCUABLE ===========================
        print()
        print("B. shape[7] IS A REGISTERED NON-RESULT -- A PERFECT NUMBER CANNOT RESCUE IT")
        rp = build_root(os.path.join(tmp, "b"), shape7_perfect=True)
        gp, _ = _grade(rp)
        s7 = gp["gates"]["G5_fd"]["PATCHED"]["per_component"]["shape[7]"]
        print("     shape[7] planted PERFECT: rel=%.6f %% two_sided=%s"
              % (s7["CD"]["rel_pct"], s7["CD"]["plateau_two_sided"]))
        unit("B1-perfect-number", True, s7["CD"]["rel_pct"] < 0.1,
             "(the planted row agrees to better than 0.1 %)")
        unit("B2-plateau-closes", True, s7["CD"]["plateau_two_sided"],
             "(and its plateau CLOSES on this planted fixture)")
        unit("B3-STILL-not-a-result", "NOT A RESULT", s7["CD"]["verdict"],
             "(AND IT IS STILL NOT A RESULT -- set from the LIST, not the value)")
        unit("B4-gate-agrees", "NOT A RESULT", gp["gates"]["G-PLAT7"]["PATCHED"]["verdict"])
        unit("B5-not-in-graded", False,
             "shape[7]" in gp["gates"]["G5_fd"]["PATCHED"]["graded_components"])
        unit("B6-four-graded", 4, gp["gates"]["G5_fd"]["PATCHED"]["n_graded_components"])
        unit("B7-published-anyway", True, s7["CD"]["rel_pct"] is not None,
             "(its reading is PUBLISHED beside the aggregate, never instead of it)")
        agg = g["gates"]["G5_fd"]["PATCHED"]["aggregate_pct_excl_flagged_CD"]
        print("     aggregate_pct_excl_flagged_CD (4 components) = %.8f %%" % agg)
        unit("B8-agg-key-named", True,
             "aggregate_pct_excl_flagged_CD" in g["gates"]["G5_fd"]["PATCHED"])

        # ============ C. THE OPTIMISER MAPPING (charter section 9) ============
        print()
        print("C. THE OPTIMISER MAPPING -- charter section 9, per row")
        unit("C1-converged", "PASS",
             g["gates"]["G-OPT9"]["PATCHED"]["verdict"],
             "(IPOPT printed `Optimal Solution Found.` -- then capped at row level)")
        rc = build_root(os.path.join(tmp, "c"), converged=False, majors=40, reduction=6.0)
        gc, _ = _grade(rc)
        unit("C2-cap-stopped", "GATE REACHED", gc["gates"]["G-OPT9"]["PATCHED"]["verdict"],
             "(cap-stopped WITH the registered intermediate threshold met)")
        unit("C3-hit-cap", True, gc["gates"]["G-OPT9"]["PATCHED"]["reached_iteration_cap"])
        rn = build_root(os.path.join(tmp, "d"), converged=False, majors=40, reduction=0.4)
        gn, _ = _grade(rn)
        unit("C4-no-threshold", "NOT A RESULT", gn["gates"]["G-OPT9"]["PATCHED"]["verdict"],
             "(cap-stopped WITHOUT the threshold -- never PASS, never `28 %% is good`)")
        unit("C5-row-not-rescued", "NOT A RESULT", gn["rows"]["PATCHED"]["verdict"],
             "(a row whose optimiser is NOT A RESULT cannot be rescued by any gate)")
        rs = build_root(os.path.join(tmp, "e"), converged=False, majors=4, reduction=9.0)
        gs, _ = _grade(rs)
        unit("C6-too-few-majors", "NOT A RESULT", gs["gates"]["G-OPT9"]["PATCHED"]["verdict"],
             "(4 majors < %d: a run of fewer than %d majors has not searched)"
             % (G.MIN_MAJORS_TO_HAVE_SEARCHED, G.MIN_MAJORS_TO_HAVE_SEARCHED))
        unit("C7-cl-travels", True,
             g["gates"]["G-OPT9"]["PATCHED"]["CL_final"] is not None,
             "(the CL pair travels with every drag number)")

        # ============ D. THE TRIVIAL BASELINE (charter section 4) =============
        print()
        print("D. THE CHARTER-4 TRIVIAL BASELINE")
        unit("D1-passes", "PASS", g["gates"]["G-TB"]["PATCHED"]["verdict"],
             "(the deliberately wrong step FAILS band D, as it must)")
        unit("D2-none-passing", 0, g["gates"]["G-TB"]["PATCHED"]["n_passing"])
        unit("D3-no-withdrawal", False,
             g["gates"]["G-TB"]["PATCHED"]["withdraws_row_fd_verdict"])

        # ============ E. THE RED LEGS ========================================
        print()
        print("E. RED LEGS -- every gate driven to FAIL")
        cases = [
            ("E1-stages-short", dict(arms=["MESH", "O-S", "XE-S", "FE-S"]),
             ("G-STAGES", "NOT A RESULT"), "item", "NOT A RESULT"),
            ("E2-np-violated", dict(ranks={"O-P": 2}),
             ("G-NP", "GATE FAIL"), "item", "GATE FAIL"),
            ("E3-cpuset", dict(cpuset={"FE-P": "0"}),
             ("G12_placement", "GATE FAIL"), "item", "GATE FAIL"),
            ("E4-so-md5", dict(so_md5={"O-P": "0" * 32}),
             ("G9_toolchain", "GATE FAIL"), "item", "GATE FAIL"),
            ("E5-over-cap", dict(core_min={"O-P": 99.0}),
             ("G10_caps", "GATE FAIL"), "item", "GATE FAIL"),
            ("E6-eval-census", dict(drop_evals=2),
             ("G-EVALFAIL", "GATE FAIL"), "item", "GATE FAIL"),
            ("E7-opt-in-endpoint", dict(plant_opt_in_endpoint=True),
             ("G-NOOPT-ENDPOINT", "GATE FAIL"), "item", "GATE FAIL"),
        ]
        for i, (name, kw, (gate, want_gate), _lvl, want_item) in enumerate(cases):
            rr = build_root(os.path.join(tmp, "red%d" % i), **kw)
            gg, rf = _grade(rr)
            if gg is None:
                unit(name, want_gate, "REFUSED:%s" % rf)
                continue
            got = gg["gates"][gate]
            got_v = got["verdict"] if isinstance(got, dict) and "verdict" in got else got
            unit(name, want_gate, got_v, "-> item %s" % gg["verdict"])
            unit(name + "-item", want_item, gg["verdict"])

        # E8: the design point.  A baseline design point is a GATE FAIL on
        # `shape_match` only if the O arm disagrees -- here both are baseline, so
        # the gate PASSES and `not_baseline` is REPORTED.  This leg proves the
        # gate is not secretly failing a converged-at-baseline optimum.
        rb = build_root(os.path.join(tmp, "f"), baseline_designpoint=True)
        gb, _ = _grade(rb)
        dp = gb["gates"]["G-DESIGNPOINT"]
        unit("E8-designpoint-ok", "PASS", dp["verdict"],
             "(matching baseline design points PASS -- the gate checks the MATCH)")
        unit("E9-not-baseline-flag", False, dp["per_arm"]["FE-P"]["not_baseline"],
             "(and `not_baseline` is REPORTED, never gated)")

        # E10: a MALFORMED artefact REFUSES; an ABSENT one is a census reading.
        rm = build_root(os.path.join(tmp, "g"), malform="FE-P")
        _gm, refm = _grade(rm)
        unit("E10-malformed-refuses", "ARTEFACT_MALFORMED", refm,
             "(a refusal is NOT A RESULT and exits 2)")
        ra = build_root(os.path.join(tmp, "h"), arms=[a for a in G.ARMS_DECLARED
                                                      if a != "FE-P"])
        ga, refa = _grade(ra)
        unit("E11-absent-no-refuse", None, refa,
             "(an ABSENT arm is a CENSUS reading, never a refusal -- L-322, D6)")
        unit("E12-absent-counted", 1, ga["gates"]["G-STAGES"]["short"])
        unit("E13-other-row-graded", True,
             ga["gates"]["G5_fd"]["SHIPPED"]["verdict"] in G.VOCAB,
             "(the arms that DID run are still graded)")

        # E14: the age guard, driven red through the comparator.
        rg = build_root(os.path.join(tmp, "i"))
        tgt = os.path.join(rg, "FE-P", "0.orig", "T")
        open(tgt, "w").write("TAMPERED\n")
        gag, _ = _grade(rg)
        unit("E14-age-guard-red", "GATE FAIL", gag["gates"]["G1_completion"]["FE-P"]["verdict"])
        unit("E15-age-refusal-named", "MANIFEST_ENTRY_MUTATED",
             gag["gates"]["G1_completion"]["FE-P"]["age_guard"]["refusal"]["REFUSE"])

        # ============ F. THE INSTRUMENT'S OWN HYGIENE ========================
        print()
        print("F. THE COMPARATOR'S OWN HYGIENE")
        gp_path = os.path.join(HERE, "d19o_grade.py")
        unit("F1-no-asserts", 0, G.count_asserts(gp_path),
             "(python3 -O strips asserts; L-332)")
        planted = os.path.join(tmp, "planted.py")
        open(planted, "w").write(open(gp_path).read() + "\ndef _p():\n    assert True\n")
        unit("F2-counter-not-blind", 1, G.count_asserts(planted),
             "(a PLANTED assert IS seen -- CLAUDE.md rule 3 applied to the counter)")
        unit("F3-ceiling-sum", G.ITEM_CEILING_CORE_MIN, sum(G.CAPS.values()),
             "(the item ceiling is Sigma(caps), asserted not restated)")
        unit("F4-seven-arms", 7, G.N_DECLARED)
        unit("F5-all-np1", {1}, set(G.ARM_RANKS.values()))
        unit("F6-gci-named", "NOT APPLICABLE", g["gates"]["GCI_roache"]["verdict"],
             "(no grid triple; rule 5 has no row to act on, and it SAYS so)")
        unit("F7-g6-named", "NOT MEASURED", g["gates"]["G6_dot_product_duality"]["verdict"])
        unit("F8-benign-counted", True,
             g["gates"]["G1_completion"]["O-P"]["benign_counts"]["simple_no_criteria"] >= 1,
             "(benign lines are COUNTED AND NAMED, never suppressed)")
        unit("F9-vocab-six", 6, len(G.VOCAB))
        unit("F10-out-mandatory", True, "--out" in open(gp_path).read())

        # ============ G. THE LIVE PLANTED-ZERO CONTROLS ======================
        print()
        print("G. THE LIVE CONTROLS -- rule 3 answered ON THE RUN ROOT, not on a fixture")
        b = g["birth_register"]
        print("     readers=%d born=%d not_born=%d ; %d of them PASS A GATE ON A ZERO"
              % (b["n_readers"], b["n_born"], b["n_not_born"],
                 b["n_readers_whose_zero_passes_a_gate"]))
        unit("G1-all-born", 0, b["n_not_born"])
        unit("G2-eight-readers", 8, b["n_readers"])
        # FIVE, not four: R2 fatal tokens, R4 optimiser markers, R5 X, R6 F, R7
        # IPOPT.  Written as 4 from memory and corrected DOWN to the driven
        # count -- the section 9.4 lesson applied to this suite's own figure.
        unit("G3-five-zero-hazards", 5, b["n_readers_whose_zero_passes_a_gate"])
        unit("G3b-hazards-named",
             ["R2_read_fatal_tokens", "R4_read_optimiser_evidence", "R5_read_X",
              "R6_read_F", "R7_read_ipopt"],
             sorted(k for k, v in b["readers"].items() if v["zero_passes_a_gate"]))
        unit("G4-all-seen", [True] * 8,
             [g["controls"][k]["seen"] for k in sorted(g["controls"])])
        unit("G5-real-targets", True,
             all(g["controls"][k]["target_kind"] == "REAL" for k in sorted(g["controls"])),
             "(on a full run every reader is born against a REAL artefact)")
        unit("G6-F-reaches-TB", True,
             g["controls"]["R6_read_F"]["n_trivial_baseline_values"] > 0,
             "(the F control reaches the steps G-TB grades, or G-TB's reader is unborn)")
        unit("G7-ipopt-both-legs", (False, True),
             (g["controls"]["R7_read_ipopt"]["negative_leg_converged"],
              g["controls"]["R7_read_ipopt"]["positive_leg_converged"]),
             "(stripped -> NOT converged; planted -> converged; same bytes otherwise)")
        unit("G8-plants-quarantined", True,
             all("grader_controls" in str(g["controls"][k].get("file", ""))
                 or "grader_controls" in str(g["controls"][k].get("files", ""))
                 or "grader_controls" in str(g["controls"][k].get("arm", "") and
                                             g["controls"][k].get("file", ""))
                 for k in ("R3_read_mesh_cells", "R5_read_X", "R6_read_F")),
             "(the plants NEVER touch a graded artefact)")

        # ---- THE RED HALF: BLIND EACH READER AND REQUIRE A REFUSAL ----------
        # A control that cannot fail is not a control.  Each leg below monkey-
        # patches ONE reader to be blind -- exactly the trailing-`\b` failure --
        # and requires grade() to REFUSE rather than compose a green verdict.
        print()
        print("H. BLINDING EACH READER MUST REFUSE, NOT GRADE")
        rblind = build_root(os.path.join(tmp, "blind"))
        blinds = [
            ("H1-blind-fatal", "read_fatal_tokens", lambda *a, **k: [],
             "ctrl_fatal_not_seen"),
            ("H2-blind-optmarker", "read_optimiser_evidence", lambda *a, **k: [],
             "ctrl_optmarker_not_seen"),
            ("H3-blind-cells", "read_mesh_cells", lambda *a, **k: None,
             "ctrl_mesh_no_target"),
            ("H4-blind-X", "read_X", lambda *a, **k: {"CD": {}, "CL": {}},
             "ctrl_X_not_seen"),
            ("H5-blind-F", "read_F", lambda *a, **k: {},
             "ctrl_F_not_seen"),
            ("H6-blind-ledger", "read_ledger", lambda *a, **k: ({}, []),
             "ctrl_ledger_reader_saw_no_rows"),
        ]
        for name, attr, fake, want_key in blinds:
            real = getattr(G, attr)
            setattr(G, attr, fake)
            try:
                _gg, ref = _grade(rblind)
            finally:
                setattr(G, attr, real)
            got = ref if ref else "NO REFUSAL -- IT GRADED ANYWAY"
            unit(name, "CONTROL", got, "(blinded %s)" % attr)
        # And the register itself must be able to report an unborn reader.
        real = G.ctrl_X
        G.ctrl_X = lambda *a, **k: {"seen": False, "target_kind": None}
        try:
            _gg2, ref2 = _grade(rblind)
        finally:
            G.ctrl_X = real
        unit("H7-unborn-refuses", "CONTROL", ref2,
             "(a reader reporting seen=False stops the grade)")

        print()
        if FAILED:
            print("D19O COMPARATOR SELFTEST: FAILED -- %d leg(s): %s" % (len(FAILED), FAILED))
            return 1
        print("D19O COMPARATOR SELFTEST: OK -- every leg driven, every red leg fired")
        print("R1, NAMED: no arm of D19O has run.  Nothing here is validated against a")
        print("real D19O artefact; a green suite is a result about the COMPARATOR.")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
